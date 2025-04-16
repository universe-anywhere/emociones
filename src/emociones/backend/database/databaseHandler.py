import sqlite3
import os
import uuid
from emociones.utils.io import getBasePath
from emociones.utils.fileUtil import calculateHash
from emociones.preferences import preferences
from emociones.constants import ATTRIBUTE_KEY_FIRMA, ATTRIBUTE_KEY_FIRMA, ATTRIBUTE_KEY_JPG
from emociones.utils.log import logInfo, logError, logWarning

class DatabaseHandler:
    def __init__(self, chatBot):
        logInfo("Iniciando DatabaseHandler")
        self.chatBot = chatBot
        base_path = getBasePath();
        
        self.db_name = os.path.join(base_path, preferences["dataBase"]["db_path"])
        logInfo(f"Conectando a la base de datos {self.db_name}...")
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        logInfo("Claves foráneas activadas.")
        self.connection.commit()
        logInfo("DatabaseHandler iniciado")


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

    def createEntity(self, entity):

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
            logError(f"Al crear la entidad: {e}")
            self.chatBot.speak(f"No se ha podido crear la entidad {entity}")
 
    def createAttribute(self, entity, attribute):
        entityKey = self.getEntity(entity)
        if entityKey is None:
            logWarning(f"No se ha podido encontrar la entidad {entity}")
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
                logError(f"Al crear el atributo: {e}")
                self.chatBot.speak(f"No se ha podido crear el atributo {attribute} para la entidad {entity}")

    def deleteEntity(self, entity):
        self.chatBot.speak(f"Eliminando entidad {entity}")
        try:
            self.cursor.execute('''
            DELETE FROM entity WHERE description = ?
            ''', (entity,))

            # Guardar los cambios y cerrar la conexión
            self.connection.commit()
            self.chatBot.speak(f"Se ha eliminado la entidad {entity}")
        except sqlite3.Error as e:
            logError(f"Al eliminar la entidad: {e}")
            self.chatBot.speak(f"No se ha podido eliminar la entidad {entity}")

    def deleteAttribute(self, entity, attribute):
        self.chatBoot.speak(f"Eliminando atributo {attribute} de la entidad {entity}")
        entityKey = self.getEntity(entity)
        if entityKey is None:
            logWarning(f"No se ha podido encontrar la entidad {entity}")
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
                logError(f"Al eliminar el atributo: {e}")
                self.chatBot.speak(f"No se ha podido eliminar el atributo {attribute} para la entidad {entity}")

    def fetchEntityUUID(self, description):
        try:
            self.cursor.execute('''
            SELECT entityUUID FROM entity
            WHERE description = ?
            ''', (description,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logError(f"Al buscar entityUUID en entity: {e}")
            return None
        
    def fetchAttributeUUID(self, description, entityDescription):
        logInfo(f"fetchAttributeUUID attribute description:  {description} de la entidad {entityDescription}.")
        try:
            self.cursor.execute('''
                SELECT attribute.attributeUUID
                FROM attribute
                    JOIN entity ON attribute.entityUUID = entity.entityUUID
                WHERE attribute.description = ? AND entity.description = ?
                ''', (description, entityDescription))

            result = self.cursor.fetchone()
            logInfo(f"fetchAttributeUUID result: {result}")
            return result[0] if result else None
        except sqlite3.Error as e:
            logError(f"Al buscar attributeUUID en attribute {description} para la entidad {entityDescription}: {e}")
            return None

    def fetchEntityInstanceUUID(self, description):
        try:
            entityUUID= self.fetchEntityUUID(description)
            if (not entityUUID is None):
                self.cursor.execute('''
                SELECT entityInstanceUUID FROM entityInstance
                WHERE entityUUID = ?
                ''', (entityUUID,))
                result = self.cursor.fetchone()
                return result[0] if result else None
            else:
                logError(f"No se pudo encontrar la instancia para entidad {description} porque no existe la entidad.")
                return None
        except sqlite3.Error as e:
            logError(f"al buscar entityInstanceUUID en entityInstance para la entidad {description}: {e}")
            return None
        
    def fetchAttributeInstanceUUIDValueText(self, description, valueText, entityDescription):
        try:
            attributeUUID= self.fetchAttributeUUID(description, entityDescription)
            if (not attributeUUID is None):
                self.cursor.execute('''
                SELECT attributeInstanceUUID FROM attributeInstance
                WHERE attributeUUID = ? AND valueText = ?
                ''', (attributeUUID,valueText))
                result = self.cursor.fetchone()
                return result[0] if result else None
            else:
                logError(f"No se pudo encontrar la instancia para el atributo {description} porque no existe como atributo.")
                return None
        except sqlite3.Error as e:
            logError(f"Al buscar attributeInstanceUUID en attributeInstance para el atributo {description}: {e}")
            return None

    def fetchAttributeInstanceUUIDValueBlob(self, entityDescription, blobHash):
        try:
            logInfo(f"Buscando la instancia para el atributo {ATTRIBUTE_KEY_FIRMA} de la entidad {entityDescription} con hash {blobHash}.")
            attributeUUID= self.fetchAttributeUUID(ATTRIBUTE_KEY_FIRMA, entityDescription)
            if (not attributeUUID is None):
                self.cursor.execute('''
                SELECT attributeInstanceUUID FROM attributeInstance
                WHERE attributeUUID = ? AND valueText = ?
                ''', (attributeUUID,blobHash))
                result = self.cursor.fetchone()
                return result[0] if result else None
            else:
                logError(f"No se pudo encontrar la instancia para el atributo {ATTRIBUTE_KEY_FIRMA} porque no existe como atributo.")
                return None
        except sqlite3.Error as e:
            logError(f"Al buscar attributeInstanceUUID en attributeInstance para el atributo {ATTRIBUTE_KEY_FIRMA}: {e}")
            return None

    def checkAttributeInstanceValueTextExists(self, value_text):
        try:
            self.cursor.execute('''
            SELECT 1 FROM attributeInstance
            WHERE valueText = ?
            ''', (value_text,))
            result = self.cursor.fetchone()
            return bool(result)
        except sqlite3.Error as e:
            logError(f"Al verificar si existe {value_text} en attributeInstance: {e}")
            return False

    def insertEntityInstance(self, entityDescription):
        try:    
            entityUUID = self.fetchEntityUUID(entityDescription)
            if (not entityUUID is None):
                entityInstanceUUID = str(uuid.uuid4())
                self.cursor.execute('''
                INSERT INTO entityInstance ( entityInstanceUUID, entityUUID) 
                                    VALUES ( ?, ? )
                ''', (entityInstanceUUID, entityUUID))
                self.connection.commit()
                logInfo(f"Instancia creada para {entityDescription}.")
                return entityInstanceUUID
            else:
                logWarning(f"No se pudo crear la instancia para {entityDescription} porque no existe como entidad.")
                return None
        except sqlite3.Error as e:
            logError(f"Al insertar en entityInstance la entidad {entityDescription}: {e}")
            return None

    def insertAttributeInstanceValueText(self, entityDescription, attributeInstanceDescription, value_text):
        self.connection.execute('BEGIN TRANSACTION')
        try:
            attributeInstanceUUID = self.fetchAttributeInstanceUUIDValueText(attributeInstanceDescription, value_text, entityDescription)    
            if (not attributeInstanceUUID is None):
                logInfo(f"Ya existe una instancia para {attributeInstanceDescription} para {value_text}")
                self.connection.rollback()
                return None
            else:
                logInfo(f"No existe una instancia para {attributeInstanceDescription} para {value_text}. Se procede a crearla.")
                entityInstanceUUID = self.insertEntityInstance(entityDescription)
                if (not entityInstanceUUID is None):
                    attributeUUID = self.fetchAttributeUUID(attributeInstanceDescription,entityDescription)
                    if (attributeUUID is None):
                        logWarning(f"No se pudo encontrar el atributo {attributeInstanceDescription} para la entidad {entityDescription}.")
                        self.connection.rollback()
                        return None
                    else:
                        attributeInstanceUUID = str(uuid.uuid4())
                        self.cursor.execute('''
                        INSERT INTO attributeInstance ( attributeInstanceUUID, valueText, attributeUUID, entityInstanceUUID) 
                                            VALUES ( ?, ?, ?, ?)
                        ''', (attributeInstanceUUID,value_text, attributeUUID, entityInstanceUUID))
                        self.connection.commit()
                        logInfo(f"Instancia creada para {value_text}.")
                        return entityInstanceUUID, attributeInstanceUUID
                else:
                    self.connection.rollback()
                    logError(f"No se pudo crear la instancia para {value_text} por problemas con la entidad {entityDescription}.")
        except sqlite3.Error as e:
            self.connection.rollback()
            logError(f"Al insertar en attributeInstance: {e}")

    def insertAttributeInstanceValueBlob(self, entityDescription, blobValue, blobHash):
        logInfo(f"Insertando blob con hash {blobHash} para la entidad {entityDescription} y blobValue Size {len(blobValue)} bytes.")
        self.connection.execute('BEGIN TRANSACTION')
        try:
            logInfo(f"Llamando a fetchAttributeInstanceUUIDValueBlob para entidad {entityDescription} y hash {blobHash}.")
            attributeInstanceUUID = self.fetchAttributeInstanceUUIDValueBlob(entityDescription, blobHash)    
            if (not attributeInstanceUUID is None):
                logInfo(f"Ya existe una instancia para {ATTRIBUTE_KEY_FIRMA} con hash {blobHash}")
                self.connection.rollback()
                return None
            else:
                logInfo(f"No existe una instancia para {ATTRIBUTE_KEY_FIRMA} con hash {blobHash}. Se procede a crearla.")
                entityInstanceUUID = self.insertEntityInstance(entityDescription)
                logInfo(f"Creada entidad {entityDescription} con entityInstanceUUID: {entityInstanceUUID}")
                if (not entityInstanceUUID is None):
                    attributeUUID = self.fetchAttributeUUID(ATTRIBUTE_KEY_FIRMA,entityDescription)
                    if (attributeUUID is None):
                        logWarning(f"No se pudo encontrar el atributo {ATTRIBUTE_KEY_FIRMA} para la entidad {entityDescription}.")
                        self.connection.rollback()
                        return None
                    else:
                        logInfo(f"Encontrado el atributo {ATTRIBUTE_KEY_FIRMA} para la entidad {entityDescription} con attributeUUID: {attributeUUID}.")
                        attributeInstanceUUID = str(uuid.uuid4())
                        logInfo(f"Creando instancia para {blobHash} con el atributo {ATTRIBUTE_KEY_FIRMA} con entityInstanceUUID {entityInstanceUUID} y attributeInstanceUUID {attributeInstanceUUID}.")
                        # creamos el atributo con el hash del blob
                        self.cursor.execute('''
                        INSERT INTO attributeInstance ( attributeInstanceUUID, valueText, attributeUUID, entityInstanceUUID) 
                                            VALUES ( ?, ?, ?, ?)
                        ''', (attributeInstanceUUID,blobHash, attributeUUID, entityInstanceUUID))

                        attributeInstanceUUID = str(uuid.uuid4())
                        attributeUUID = self.fetchAttributeUUID(ATTRIBUTE_KEY_JPG,entityDescription)
                        if (attributeUUID is None):
                            logWarning(f"No se pudo encontrar el atributo {ATTRIBUTE_KEY_JPG} para la entidad {entityDescription}.")
                            self.connection.rollback()
                            return None
                        else:
                            logInfo(f"Creando instancia para blob con el atributo {ATTRIBUTE_KEY_JPG} y attributeInstanceUUID {attributeInstanceUUID}.")
                            # creamos el atributo con el contenido del blob
                            self.cursor.execute('''
                            INSERT INTO attributeInstance ( attributeInstanceUUID, valueBlob, attributeUUID, entityInstanceUUID) 
                                                VALUES ( ?, ?, ?, ?)
                            ''', (attributeInstanceUUID,blobValue, attributeUUID, entityInstanceUUID))
                        self.connection.commit()
                        logInfo(f"Instancia creada para {blobHash}.")
                else:
                    self.connection.rollback()
                    logError(f"No se pudo crear la instancia para {blobHash} por problemas con la entidad {entityDescription}.")
        except sqlite3.Error as e:
            self.connection.rollback()
            logError(f"Al insertar en attributeInstance: {e}")


    def getAttributeInstanceEntityInstanceUUIDFromValueText(self, value_text):
        try:
            self.cursor.execute('''
            SELECT entityInstanceUUID FROM attributeInstance
            WHERE valueText = ?
            ''', (value_text,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logError(f"Al buscar attribute_instance_UUIDs en attributeInstance para {value_text}: {e}")
        
    def insertFileHash(self, file_path, entityDescription):
        try:
            file_hash = calculateHash(file_path)
            if file_hash:
                attributeInstanceUUID = str(uuid.uuid4())
                attributeUUID = self.fetchAttributeUUID(ATTRIBUTE_KEY_FIRMA, entityDescription)
                if attributeUUID is None:
                    logWarning(f"No se pudo encontrar el atributo {ATTRIBUTE_KEY_FIRMA} para la entidad {entityDescription}.")
                    return
                entityInstanceUUID = self.getAttributeInstanceEntityInstanceUUIDFromValueText(file_path)
                
                if entityInstanceUUID is None:
                    logWarning(f"No se pudo crear la instancia de entidad para {entityDescription}.")
                    return
                self.cursor.execute('''
                INSERT INTO attributeInstance (attributeInstanceUUID, valueText, attributeUUID, entityInstanceUUID)
                VALUES (?, ?, ?, ?)
                ''', (attributeInstanceUUID, file_hash, attributeUUID, entityInstanceUUID))
                self.connection.commit()
                logInfo(f"Hash del archivo {file_path} insertado correctamente.")
            else:
                logWarning(f"No se pudo calcular el hash para el archivo {file_path}.")
        except sqlite3.Error as e:
            logError(f"Al insertar atributo {ATTRIBUTE_KEY_FIRMA} del archivo {file_path} para la entidad {entityDescription}: {e}")

    def getRelationshipUUID(self, relationshipDescription):
        logInfo(f"Buscando relationshipUUID de la relación {relationshipDescription} en la base de datos.")
        # Obtener la relación de la base de datos
        self.cursor.execute('''
        SELECT relationshipUUID FROM relationship WHERE description = ?
        ''', (relationshipDescription,))

        result = self.cursor.fetchone()
        if result:
            relationshipUUID = result[0]
            return relationshipUUID
        else:
            return None
        
    def insertRelationship(self, relationShipDescription, entityInstanceUUID1, entityInstanceUUID2):
        relationshipUUID = self.getRelationshipUUID(relationShipDescription)
        if relationshipUUID is None:
            logWarning(f"No se pudo encontrar la relación {relationShipDescription} en la base de datos.")
            return None
        
        try:
            logInfo(f"Insertando relación {relationShipDescription} con relationshipUUID {relationshipUUID}, entityInstanceUUID1 {entityInstanceUUID1} y entityInstanceUUID2 {entityInstanceUUID2}.")
            # Generar un UUID único para la relación
            relationshipInstanceUUID = str(uuid.uuid4())
            # Insertar la relación en la tabla relationshipInstance
            self.cursor.execute('''
                    INSERT INTO entitiesRelationShipInstance (entitiesRelationshipInstanceUUID, relationshipUUID, 
                                entityInstanceUUID1, entityInstanceUUID2)  values (?, ?, ?, ?)
            ''', (relationshipInstanceUUID, relationshipUUID, entityInstanceUUID1, entityInstanceUUID2))
            # Guardar los cambios y cerrar la conexión
            self.connection.commit()
            logInfo(f"Relación {relationShipDescription} insertada correctamente con relationshipInstanceUUID {relationshipInstanceUUID}.")
        except sqlite3.Error as e:
            logError(f"Al insertar en relationship {relationShipDescription} con relationshipUUID {relationshipUUID}, entityInstanceUUID1 {entityInstanceUUID1} y entityInstanceUUID2 {entityInstanceUUID2} -> {e}")
    def close(self):
        self.connection.close()

    def __del__(self):
        # Llamar a close() automáticamente al destruir la instancia
        self.close()
