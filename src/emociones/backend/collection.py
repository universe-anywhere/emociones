import os
import mimetypes
from emociones.preferences import preferences 
from emociones.globals.globalVars import app_context
from emociones.constants import ATTRIBUTE_KEY_RUTA, ATTRIBUTE_KEY_FIRMA
from emociones.utils.log import log_info, log_error, log_warning

class Collection:
    def __init__(self):
        pass
    def refreshCollection(self):
        app_context.chatBoot.speak("Actualizando la colección...")
        collectionPath = preferences["gallery"]["galleryPath"]
        try:
            log_info(f"Recorriendo la colección en {collectionPath}...")
            for root, _, files in os.walk(collectionPath):
                for file in files:
                    file_path = os.path.abspath(os.path.join(root, file))

                    # Determinar el tipo MIME
                    file_type, _ = mimetypes.guess_type(file_path)
                    log_info(f"Tipo MIME: {file_type}","Archivo: {file_path}")
                    if file_type:
                        if file_type.startswith('image'):
                            description = "imagen"
                        elif file_type.startswith('video'):
                            description = "video"
                        else:
                            continue

                        # Verificar si ya existe en attributeinstance
                        log_info(f"Verificando si existe {file_path} en attributeinstance")
                        if app_context.dbHandler.check_attribute_instance_value_text_exists(file_path):
                            log_info(f"{file_path} ya existe en attributeinstance. Se pasa al siguiente archivo.")
                            continue

                        # Obtener attributeUUID
                        log_info(f"Buscando attributeUUID {ATTRIBUTE_KEY_RUTA} para {description}...")
                        attributeUUID = app_context.dbHandler.fetch_attribute_uuid(ATTRIBUTE_KEY_RUTA,description)
                        if not attributeUUID:
                            log_warning(f"No se encontró attributeUUID para {description}: {ATTRIBUTE_KEY_RUTA}")
                            continue

                        # Insertar nueva instancia
                        log_info(f"Insertando nueva instancia para {description} con el atributo {ATTRIBUTE_KEY_RUTA}")
                        app_context.dbHandler.insert_attribute_instance_valueText(description, ATTRIBUTE_KEY_RUTA, file_path)
                        
                        log_info(f"Insertando nueva instancia para {description} con el atributo {ATTRIBUTE_KEY_FIRMA}")
                        app_context.dbHandler.insert_file_hash(file_path, description)
                        
                        log_info(f"Procesando siguiente archivo")
            
            app_context.chatBoot.speak("Se ha actualizado la colección.")     
            log_info("Archivos procesados correctamente.")
        except Exception as e:
            app_context.chatBoot.speak("Ocurrió un error al actualzar la colección.")
            log_error("Ocurrió un error: {e}")