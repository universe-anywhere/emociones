import sqlite3
import os
from emociones.utils.io import get_base_path
from emociones.preferences import preferences

class DatabaseHandler:
    def __init__(self):
        base_path = get_base_path();
        self.db_name = os.path.join(base_path, preferences["dataBase"]["db_path"])
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.connection.commit()

        print("Claves foráneas activadas.")

    def create_entity(self, entity):
        print("Creando entidad:", entity)
#        self.cursor.execute("INSERT INTO entity (name) VALUES (?)", (name,))
#        self.connection.commit()

    def create_attribute(self, entity, attribute):
        print("Creando atributo:", attribute, "en entidad:", entity)
#        self.cursor.execute("INSERT INTO attribute (entity_id, name) VALUES (?, ?)", (entity_id, name))
#        self.connection.commit()

    def delete_entity(self, entity):
        print("Eliminando entidad:", entity)

    def delete_attribute(self, entity, attribute):
        print("Eliminando atributo:", attribute, "en entidad:", entity)

    def close(self):
        self.connection.close()

    def __del__(self):
        # Llamar a close() automáticamente al destruir la instancia
        self.close()
