import sqlite3
import os
import uuid
from emociones.utils.io import get_base_path
from emociones.utils.fileUtil import calcular_hash
from emociones.preferences import preferences
from emociones.constants import ATTRIBUTE_KEY_FIRMA

class DatabaseHandler:
    def __init__(self, chatBot):
        self.chatBot = chatBot
        base_path = get_base_path();
        self.db_name = os.path.join(base_path, preferences["dataBase"]["db_path"])
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.connection.commit()

        print("Claves foráneas activadas.")

    def getEntity(self, entityDescription):
        # Obtener la entidad de la base de datos
        self.cursor.execute('''
        SELECT entityUUID FROM entity WHERE description = ?
        ''', (entityDescription,))

        result = self.cursor.fetchone()
        if result:
            entityUUID = result[0]
            return entityUUID
        else:
            return None

    def create_entity(self, entity):

        self.chatBot.speak(f"Creando entidad {entity}")
        try:
            self.cursor.execute('''
            INSERT INTO entity (entityUUID, description)
            VALUES (?, ?)
            ''', (str(uuid.uuid4()), entity))

            # Guardar los cambios y cerrar la conexión
            self.connection.commit()
            self.chatBot.speak(f"Se ha creado la entidad {entity}")
        except sqlite3.Error as e:
            print("Error al crear la entidad:", e)
            self.chatBot.speak(f"No se ha podido crear la entidad {entity}")
 
    def create_attribute(self, entity, attribute):
        entityKey = self.getEntity(entity)
        if entityKey is None:
            self.chatBot.speak(f"No se ha podido encontrar la entidad {entity}")
        else:
            try:
                self.cursor.execute('''
                INSERT INTO attribute (attributeUUID, description, entityUUID)
                VALUES (?, ?, ?)
                ''', (str(uuid.uuid4()), attribute, entityKey))

                # Guardar los cambios y cerrar la conexión
                self.connection.commit()
                self.chatBot.speak(f"Se ha creado el atributo {attribute} para la entidad {entity}")
            except sqlite3.Error as e:
                print("Error al crear el atributo:", e)
                self.chatBot.speak(f"No se ha podido crear el atributo {attribute} para la entidad {entity}")

    def delete_entity(self, entity):
        self.chatBot.speak(f"Eliminando entidad {entity}")
        try:
            self.cursor.execute('''
            DELETE FROM entity WHERE description = ?
            ''', (entity,))

            # Guardar los cambios y cerrar la conexión
            self.connection.commit()
            self.chatBot.speak(f"Se ha eliminado la entidad {entity}")
        except sqlite3.Error as e:
            print("Error al eliminar la entidad:", e)
            self.chatBot.speak(f"No se ha podido eliminar la entidad {entity}")

    def delete_attribute(self, entity, attribute):
        self.chatBoot.speak(f"Eliminando atributo {attribute} de la entidad {entity}")
        entityKey = self.getEntity(entity)
        if entityKey is None:
            self.chatBot.speak(f"No se ha podido encontrar la entidad {entity}")
        else:
            try:
                self.cursor.execute('''
                DELETE FROM attribute WHERE description = ? AND entityUUID = ?
                ''', (attribute, entityKey))

                # Guardar los cambios y cerrar la conexión
                self.connection.commit()
                self.chatBot.speak(f"Se ha eliminado el atributo {attribute} para la entidad {entity}")
            except sqlite3.Error as e:
                print("Error al eliminar el atributo:", e)
                self.chatBot.speak(f"No se ha podido eliminar el atributo {attribute} para la entidad {entity}")

    def fetch_entity_uuid(self, description):
        try:
            self.cursor.execute('''
            SELECT entityUUID FROM entity
            WHERE description = ?
            ''', (description,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error al buscar entityUUID en entity: {e}")
            return None
        
    def fetch_attribute_uuid(self, description, entityDescription):
        try:
            self.cursor.execute('''
                SELECT attribute.attributeUUID
                FROM attribute
                    JOIN entity ON attribute.entityUUID = entity.entityUUID
                WHERE attribute.description = ? AND entity.description = ?
                ''', (description, entityDescription))

            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error al buscar attributeUUID en attribute: {e}")
            return None

    def fetch_entityInstance_uuid(self, description):
        try:
            entityUUID= self.fetch_entity_uuid(description)
            if (not entityUUID is None):
                self.cursor.execute('''
                SELECT entityInstanceUUID FROM entityInstance
                WHERE entityUUID = ?
                ''', (entityUUID,))
                result = self.cursor.fetchone()
                return result[0] if result else None
            else:
                print(f"No se pudo buscar la instancia para {description} porque no existe como entidad.")
                return None
        except sqlite3.Error as e:
            print(f"Error al buscar entityInstanceUUID en entityInstance: {e}")
            return None
        
    def fetch_attributeInstance_uuid_valueText(self, description, valueText, entityDescription):
        try:
            attributeUUID= self.fetch_attribute_uuid(description, entityDescription)
            if (not attributeUUID is None):
                self.cursor.execute('''
                SELECT attributeInstanceUUID FROM attributeInstance
                WHERE attributeUUID = ? AND valueText = ?
                ''', (attributeUUID,valueText))
                result = self.cursor.fetchone()
                return result[0] if result else None
            else:
                print(f"No se pudo buscar la instancia para {description} porque no existe como atributo.")
                return None
        except sqlite3.Error as e:
            print(f"Error al buscar attributeInstanceUUID en attributeInstance: {e}")
            return None

    def check_attribute_instance_value_text_exists(self, value_text):
        try:
            self.cursor.execute('''
            SELECT 1 FROM attributeInstance
            WHERE valueText = ?
            ''', (value_text,))
            result = self.cursor.fetchone()
            return bool(result)
        except sqlite3.Error as e:
            print(f"Error al verificar attributeInstance: {e}")
            return False

    def insert_entityInstance(self, entityDescription):
        try:    
            entityUUID = self.fetch_entity_uuid(entityDescription)
            if (not entityUUID is None):
                entityInstanceUUID = str(uuid.uuid4())
                self.cursor.execute('''
                INSERT INTO entityInstance ( entityInstanceUUID, entityUUID) 
                                    VALUES ( ?, ? )
                ''', (entityInstanceUUID, entityUUID))
                self.connection.commit()
                print(f"Instancia creada para {entityDescription}.")
                return entityInstanceUUID
            else:
                print(f"No se pudo crear la instancia para {entityDescription} porque no existe como entidad.")
                return None
        except sqlite3.Error as e:
            print(f"Error al insertar en entityInstance: {e}")
            return None

    def insert_attribute_instance_valueText(self, entityDescription, attributeInstanceDescription, value_text):
        self.connection.execute('BEGIN TRANSACTION')
        try:
            attributeInstanceUUID = self.fetch_attributeInstance_uuid_valueText(attributeInstanceDescription, value_text, entityDescription)    
            if (not attributeInstanceUUID is None):
                print(f"Ya existe una instancia para {attributeInstanceDescription} para {value_text}")
                self.connection.rollback()
                return None
            else:
                print(f"No existe una instancia para {attributeInstanceDescription}. Se procede a crearla.")
                entityInstanceUUID = self.insert_entityInstance(entityDescription)
                if (not entityInstanceUUID is None):
                    attributeUUID = self.fetch_attribute_uuid(attributeInstanceDescription,entityDescription)
                    if (attributeUUID is None):
                        print(f"Error no existe el atribute {attributeInstanceDescription} para la entidad {entityDescription}.")
                        self.connection.rollback()
                        return None
                    else:
                        attributeInstanceUUID = str(uuid.uuid4())
                        self.cursor.execute('''
                        INSERT INTO attributeInstance ( attributeInstanceUUID, valueText, attributeUUID, entityInstanceUUID) 
                                            VALUES ( ?, ?, ?, ?)
                        ''', (attributeInstanceUUID,value_text, attributeUUID, entityInstanceUUID))
                        self.connection.commit()
                        print(f"Instancia creada para {value_text}.")
                else:
                    self.connection.rollback()
                    print(f"No se pudo crear la instancia para {value_text} por problemas con la entidad {entityDescription}.")    
        except sqlite3.Error as e:
            self.connection.rollback()
            print(f"Error al insertar en attributeInstance: {e}")

    def get_attribute_instance_entityInstanceUUID_from_valueText(self, value_text):
        try:
            self.cursor.execute('''
            SELECT entityInstanceUUID FROM attributeInstance
            WHERE valueText = ?
            ''', (value_text,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error al buscar attribute_instance_UUIDs en attributeInstance: {e}")
            return None
        
    def insert_file_hash(self, file_path, entityDescription):
        try:
            file_hash = calcular_hash(file_path)
            if file_hash:
                attributeInstanceUUID = str(uuid.uuid4())
                attributeUUID = self.fetch_attribute_uuid(ATTRIBUTE_KEY_FIRMA, entityDescription)
                if attributeUUID is None:
                    print(f"Error: No se pudo encontrar el atributo {ATTRIBUTE_KEY_FIRMA} para la entidad {entityDescription}.")
                    return
                entityInstanceUUID = self.get_attribute_instance_entityInstanceUUID_from_valueText(file_path)
                
                if entityInstanceUUID is None:
                    print(f"Error: No se pudo crear la instancia de entidad para {entityDescription}.")
                    return
                self.cursor.execute('''
                INSERT INTO attributeInstance (attributeInstanceUUID, valueText, attributeUUID, entityInstanceUUID)
                VALUES (?, ?, ?, ?)
                ''', (attributeInstanceUUID, file_hash, attributeUUID, entityInstanceUUID))
                self.connection.commit()
                print(f"Hash del archivo {file_path} insertado correctamente.")
            else:
                print(f"No se pudo calcular el hash para el archivo {file_path}.")
        except sqlite3.Error as e:
            print(f"Error al insertar el hash del archivo: {e}")

    def close(self):
        self.connection.close()

    def __del__(self):
        # Llamar a close() automáticamente al destruir la instancia
        self.close()
