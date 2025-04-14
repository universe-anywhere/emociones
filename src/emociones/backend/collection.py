import os
import mimetypes
from emociones.preferences import preferences 
from emociones.globals.globalVars import app_context
from emociones.constants import ATTRIBUTE_KEY_RUTA, ATTRIBUTE_KEY_FIRMA

class Collection:
    def __init__(self):
        pass
    def refreshCollection(self):
        app_context.chatBoot.speak("Actualizando la colección...")
        collectionPath = preferences["gallery"]["galleryPath"]
        try:
            print(f"Recorriendo la colección en {collectionPath}...")
            for root, _, files in os.walk(collectionPath):
                for file in files:
                    file_path = os.path.abspath(os.path.join(root, file))

                    # Determinar el tipo MIME
                    file_type, _ = mimetypes.guess_type(file_path)
                    print(f"Tipo MIME: {file_type}","Archivo: {file_path}")
                    if file_type:
                        if file_type.startswith('image'):
                            description = "imagen"
                        elif file_type.startswith('video'):
                            description = "video"
                        else:
                            continue

                        # Verificar si ya existe en attributeinstance
                        print(f"Verificando si existe {file_path} en attributeinstance")
                        if app_context.dbHandler.check_attribute_instance_value_text_exists(file_path):
                            print(f"{file_path} ya existe en attributeinstance. Se pasa al siguiente archivo.")
                            continue

                        # Obtener attributeUUID
                        print(f"Buscando attributeUUID {ATTRIBUTE_KEY_RUTA} para {description}...")
                        attributeUUID = app_context.dbHandler.fetch_attribute_uuid(ATTRIBUTE_KEY_RUTA,description)
                        if not attributeUUID:
                            print(f"No se encontró attributeUUID para description: {ATTRIBUTE_KEY_RUTA}")
                            continue

                        # Insertar nueva instancia
                        print(f"Insertando nueva instancia para {description} con el atributo {ATTRIBUTE_KEY_RUTA}")
                        app_context.dbHandler.insert_attribute_instance_valueText(description, ATTRIBUTE_KEY_RUTA, file_path)
                        print(f"Insertando nueva instancia para {description} con el atributo {ATTRIBUTE_KEY_FIRMA}")
                        app_context.dbHandler.insert_file_hash(file_path, description)
                        print(f"Procesando siguiente archivo...")
            app_context.chatBoot.speak("Se ha actualizado la colección.")            
            print("Archivos procesados correctamente.")
        except Exception as e:
            app_context.chatBoot.speak("Ocurrió un error al actualzar la colección.")
            print(f"Ocurrió un error: {e}")