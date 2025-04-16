import threading
import os
from emociones.preferences import preferences 
from emociones.globals.globalVars import app_context
from emociones.constants import ENTITY_KEY_FOTO, ENTITY_KEY_VIDEO, IMAGE
from emociones.utils.log import logInfo, logError, logWarning
from emociones.utils.fileUtil import isValidFile
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

                        # Determinar el tipo MIME
                        description = ENTITY_KEY_FOTO if validFile[1] == IMAGE else ENTITY_KEY_VIDEO
                        logInfo(f"Verificando si existe {file_path} en attributeinstance")
                        if dbHandler.checkAttributeInstanceValueTextExists(file_path):
                            logInfo(f"{file_path} ya existe en attributeinstance. Se pasa al siguiente archivo.")
                            continue

                        # Insertar nueva instancia y manejar relaciones como en el código original
                        logInfo(f"Insertando nueva instancia para {description}")
                        # Código original para la inserción aquí...

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

    def stopDetection(self):
        """Detiene el proceso de actualización."""
        if self.isRunning:
            logInfo("Solicitando detención del hilo de actualización...")
            self.stop_event.set()  # Activar el evento para detener el hilo
        else:
            logInfo("No hay procesos en ejecución para detener.")

    def waitForCompletion(self):
        """Espera a que el hilo de actualización termine."""
        if self.processingThread:
            self.processingThread.join()