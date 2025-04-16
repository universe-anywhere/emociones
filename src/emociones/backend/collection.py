import os
from emociones.preferences import preferences 
from emociones.globals.globalVars import app_context
from emociones.constants import ATTRIBUTE_KEY_RUTA, ATTRIBUTE_KEY_FIRMA, ENTITY_KEY_FOTO, ENTITY_KEY_VIDEO, IMAGE, VIDEO, RELATIONSHIP_KEY_MULTIMEDIA,ENTITY_KEY_IMAGE
from emociones.utils.log import logInfo, logError, logWarning
from emociones.utils.fileUtil import isValidFile

class Collection:
    def __init__(self):
        pass

    def refreshCollection(self):
        app_context.chatBoot.speak("Actualizando la colección...")
        collectionPath = preferences["gallery"]["galleryPath"]
        try:
            logInfo(f"Recorriendo la colección en {collectionPath}...")
            for root, _, files in os.walk(collectionPath):
                logInfo(f"Procesando directorio: {root}")
                for file in files:
                    file_path = os.path.abspath(os.path.join(root, file))
                    validFile = isValidFile(file_path)
                    if (not validFile):
                        logWarning(f"Archivo no válido: {file_path}")
                        continue

                    # Determinar el tipo MIME
                    if (validFile[1] == IMAGE):
                        description = ENTITY_KEY_FOTO
                    elif (validFile[1] == VIDEO):
                        description = ENTITY_KEY_VIDEO

                    # Verificar si ya existe en attributeinstance
                    logInfo(f"Verificando si existe {file_path} en attributeinstance")
                    if app_context.dbHandler.checkAttributeInstanceValueTextExists(file_path):
                        logInfo(f"{file_path} ya existe en attributeinstance. Se pasa al siguiente archivo.")
                        continue

                    # Obtener attributeUUID
                    logInfo(f"Buscando attributeUUID {ATTRIBUTE_KEY_RUTA} para {description}...")
                    attributeUUID = app_context.dbHandler.fetchAttributeUUID(ATTRIBUTE_KEY_RUTA,description)
                    if not attributeUUID:
                        logWarning(f"No se encontró attributeUUID para {description}: {ATTRIBUTE_KEY_RUTA}")
                        continue

                    # Insertar nueva instancia
                    logInfo(f"Insertando nueva instancia para {description} con el atributo {ATTRIBUTE_KEY_RUTA}")
                    instances = app_context.dbHandler.insertAttributeInstanceValueText(description, ATTRIBUTE_KEY_RUTA, file_path)
                        
                    logInfo(f"Insertando nueva instancia para {description} con el atributo {ATTRIBUTE_KEY_FIRMA}")
                    app_context.dbHandler.insertFileHash(file_path, description)

                    app_context.dbHandler.connection.execute('BEGIN TRANSACTION')
                    #Insertar nueva instancia de relacion Archivo Multimedia
                    entityInstanceUUID1 = app_context.dbHandler.insertEntityInstance(ENTITY_KEY_IMAGE)
                    if not entityInstanceUUID1:
                        logWarning(f"No se pudo insertar la instancia de entidad para {ENTITY_KEY_IMAGE}")
                        app_context.dbHandler.connection.rollback()
                        continue    
                    else:
                        try:                        
                            logInfo(f"Insertando nueva instancia de relación {RELATIONSHIP_KEY_MULTIMEDIA} para entidad {description}")
                            app_context.dbHandler.insertRelationship(RELATIONSHIP_KEY_MULTIMEDIA,entityInstanceUUID1, instances[0])
                            app_context.dbHandler.connection.commit()
                        except Exception as e:  
                            logError(f"Error al insertar la relación {RELATIONSHIP_KEY_MULTIMEDIA} para la entidad {description}: {e}")
                            app_context.dbHandler.connection.rollback()
                            continue    
                    logInfo(f"Procesando siguiente archivo")
                logInfo(f"Directorio procesado: {root}")
                            
            app_context.chatBoot.speak("Se ha actualizado la colección.")     
            logInfo("Archivos procesados correctamente.")
        except Exception as e:
            app_context.chatBoot.speak("Ocurrió un error al actualzar la colección.")
            logError("Ocurrió un error: {e}")

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
                    logInfo(f"Procesando siguiente archivo")
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