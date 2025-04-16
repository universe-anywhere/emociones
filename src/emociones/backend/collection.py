import threading
import os
from emociones.preferences import preferences 
from emociones.globals.globalVars import app_context
from emociones.constants import ENTITY_KEY_MULTIMEDIA, IMAGE, VIDEO
from emociones.utils.log import logInfo, logError, logWarning
from emociones.utils.fileUtil import isValidFile, fileType
from emociones.backend.database.databaseHandler import DatabaseHandler

class Collection:
    def __init__(self):
        logInfo("Iniciando Collection")
        self.isRunning = False  # Bandera para evitar múltiples ejecuciones
        self.processingThread = None  # Hilo de procesamiento
        self.stop_event = threading.Event()  # Evento para detener el hilo
        logInfo("Collection iniciada")

    def refreshCollection(self):
        """Actualiza la colección en un hilo separado."""
        if self.isRunning:
            app_context.chatBoot.speak("El proceso de actualización ya está en ejecución. Por favor, espera.")
            logWarning("Actualización ya en ejecución.")
            return
        
        def runUpdate():
            self.isRunning = True
            self.stop_event.clear()
            app_context.chatBoot.speak("Iniciando la actualización de la colección...")
            dbHandler = DatabaseHandler(app_context.chatBoot)  # Acceso al manejador de base de datos

            collectionPath = preferences["gallery"]["galleryPath"]
            try:
                logInfo(f"Recorriendo la colección en {collectionPath}...")
                for root, _, files in os.walk(collectionPath):
                    logInfo(f"Procesando directorio: {root}")
                    for file in files:
                        if self.stop_event.is_set():  # Detener si el evento está activado
                            logInfo("Detención manual solicitada. Finalizando hilo de actualización.")
                            return
                        
                        file_path = os.path.abspath(os.path.join(root, file))
                        validFile = isValidFile(file_path)
                        if not validFile:
                            logWarning(f"Archivo no válido: {file_path}")
                            continue

                        logInfo(f"Verificando si existe {file_path} en attributeinstance")
                        if dbHandler.checkAttributeInstanceValueTextExists(file_path):
                            logInfo(f"{file_path} ya existe en attributeinstance. Se pasa al siguiente archivo.")
                            continue

                        # Determinar el tipo MIME
                        file_type = fileType(file_path)
                        self.description = None
                        if file_type == IMAGE:
                            self.description = ENTITY_KEY_MULTIMEDIA
                        elif file_type == VIDEO: 
                            self.description = ENTITY_KEY_MULTIMEDIA

                        if self.description is None:
                            logWarning(f"Formato no soportado para {file_path}.")
                            continue

                        dbHandler.connection.execute("BEGIN TRANSACTION")
                        try:
                            dbHandler.aggregateFileToDatabasecollection(self.description,file_path)
                            dbHandler.connection.commit()
                            logInfo(f"Archivo {file_path} agregado a la base de datos.")
                        except Exception as e:
                            dbHandler.connection.roollback()
                            logError(f"Error al agregar {file_path} a la base de datos: {e}")   
                    logInfo(f"Directorio procesado: {root}")

                app_context.chatBoot.speak("Se ha actualizado la colección.")
                logInfo("Archivos procesados correctamente.")
            except Exception as e:
                app_context.chatBoot.speak("Ocurrió un error al actualizar la colección.")
                logError(f"Error: {e}")
            finally:
                self.isRunning = False
                logInfo("Proceso de actualización finalizado.")

        # Ejecutar el proceso en un hilo separado
        self.processingThread = threading.Thread(target=runUpdate)
        self.processingThread.start()
        logInfo("Actualización lanzada en un hilo separado.")

    def getCollectionFromFolder(self, collectionPath):
        """
        Obtiene la colección de imágenes y videos.
        """
        collection = []
        recursive_loading = preferences["gallery"]["recursive_loading"]
        logInfo(f"Recorriendo la colección en {collectionPath} con modo recursivo: {recursive_loading}")
        try:
            for root, dirs, files in os.walk(collectionPath):
                logInfo(f"Procesando directorio: {root}")
                for file in files:
                    file_path = os.path.abspath(os.path.join(root, file))
                    validFile = isValidFile(file_path)
                    if (not validFile):
                        logWarning(f"Archivo no válido: {file_path}")
                        continue
                    collection.append(file_path)   
                    logInfo(f"Añadido archivo a la colección: {file_path}")                     
                logInfo(f"Directorio procesado: {root}")
                if (recursive_loading == False):
                    # Limpiar la lista de subcarpetas para evitar que os.walk entre en ellas
                    del dirs[:]
                            
            app_context.chatBoot.speak("Se ha obtenido toda la colección.")     
            logInfo("Se ha obtenido toda la colección.")
        
            return collection
        except Exception as e:
            app_context.chatBoot.speak("Ocurrió un error al obtener la colección.")
            logError("Al obtener la colección: {e}")
            
    def stopDetection(self):
        """Detiene el proceso de actualización."""
        if self.isRunning:
            logInfo("Solicitando detención del hilo de actualización...")
            self.stop_event.set()  # Activar el evento para detener el hilo

            if self.processingThread:
                self.processingThread.join()  # Esperar a que el hilo termine
            self.isRunning = False
        else:
            logInfo("No hay procesos en ejecución para detener.")

    def waitForCompletion(self):
        """Espera a que el hilo de actualización termine."""
        if self.processingThread:
            self.processingThread.join()