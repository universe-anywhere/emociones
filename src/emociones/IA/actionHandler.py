from emociones.database.databaseHandler import DatabaseHandler
from emociones.IA.chatbotInterpreter import ChatbotInterpreter

class ActionHandler:
    def __init__(self, chatBoot):
        self.db = DatabaseHandler()
        self.interpreter = ChatbotInterpreter()
        self.chatBootInstance = chatBoot  # Guardar la instancia de ChatBot

    def handle_text(self, text):
        # Interpretar el texto
        interpretation = self.interpreter.interpret(text)
        print(f"Interpretación obtenida: {interpretation}")  # Para depuración

        # Extraer la acción y los parámetros
        action = interpretation["action"]
        parameters = interpretation["parameters"]

        if action == "create_entity":
            # Obtener los parámetros necesarios
            entity = parameters.get("entity")
            if entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres crear la entidad {entity}?"
                respuesta = self.chatBootInstance.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    self.chatBootInstance.speak("Trabajando...")
                    self.db.create_entity(entity)
                    self.chatBootInstance.speak(f"Se ha creado la entidad {entity}")
                else:
                    self.chatBootInstance.speak("De acuerdo, no se creará la entidad")
            else:
                self.chatBootInstance.speak("No he entendido bien la información para crear la entidad")

        elif action == "create_attribute":
            # Obtener los parámetros necesarios
            attribute = parameters.get("attribute")
            entity = parameters.get("entity")

            if attribute and entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres crear el atributo {attribute} para la entidad {entity}?"
                respuesta = self.chatBootInstance.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    self.chatBootInstance.speak("Trabajando...")
                    self.db.create_attribute(entity, attribute)
                    self.chatBootInstance.speak(f"Se ha creado el atributo {attribute} para la entidad {entity}")
                else:
                    self.chatBootInstance.speak("De acuerdo, no se creará el atributo")
            else:
                self.chatBootInstance.speak("No he entendido bien la información para crear el atributo")

        elif action == "delete_entity":
            # Obtener los parámetros necesarios
            entity = parameters.get("entity")
            if entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres eliminar la entidad {entity}?"
                respuesta = self.chatBootInstance.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    self.chatBootInstance.speak("Trabajando...")
                    self.db.delete_entity(entity)
                    self.chatBootInstance.speak(f"Se ha eliminado la entidad {entity}")
                else:
                    self.chatBootInstance.speak("De acuerdo, no se eliminará la entidad")
            else:
                self.chatBootInstance.speak("No he entendido bien la información para eliminar la entidad")

        elif action == "delete_attribute":
            # Obtener los parámetros necesarios
            attribute = parameters.get("attribute")
            entity = parameters.get("entity")

            if attribute and entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres eliminar el atributo {attribute} de la entidad {entity}?"
                respuesta = self.chatBootInstance.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    self.chatBootInstance.speak("Trabajando...")
                    self.db.delete_attribute(entity, attribute)
                    self.chatBootInstance.speak(f"Se ha eliminado el atributo {attribute} de la entidad {entity}")
                else:
                    self.chatBootInstance.speak("De acuerdo, no se eliminará el atributo")
            else:
                self.chatBootInstance.speak("No he entendido bien la información para eliminar el atributo")

        else:
            # Caso para acciones desconocidas
            self.chatBootInstance.speak("Lo siento, no te he entendido")
            print("Acción desconocida.")

    def close(self):
        self.db.close()
