from emociones.IA.chatbotInterpreter import ChatbotInterpreter
from emociones.globals.globalVars import app_context
from emociones.backend.collection import Collection
from emociones.utils.log import log_info, log_warning

class ActionHandler:
    def __init__(self):
        self.interpreter = ChatbotInterpreter()

    def handle_text(self, text):
        # Interpretar el texto
        interpretation = self.interpreter.interpret(text)
        log_info(f"Interpretación obtenida: {interpretation}")  # Para depuración

        # Extraer la acción y los parámetros
        action = interpretation["action"]
        parameters = interpretation["parameters"]

        if action == "create_entity":
            # Obtener los parámetros necesarios
            entity = parameters.get("entity")
            if entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres crear la entidad {entity}?"
                respuesta = app_context.chatBoot.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.create_entity(entity)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se creará la entidad")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para crear la entidad")

        elif action == "create_attribute":
            # Obtener los parámetros necesarios
            attribute = parameters.get("attribute")
            entity = parameters.get("entity")

            if attribute and entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres crear el atributo {attribute} para la entidad {entity}?"
                respuesta = app_context.chatBoot.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.create_attribute(entity, attribute)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se creará el atributo")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para crear el atributo")

        elif action == "delete_entity":
            # Obtener los parámetros necesarios
            entity = parameters.get("entity")
            if entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres eliminar la entidad {entity}?"
                respuesta = app_context.chatBoot.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.delete_entity(entity)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se eliminará la entidad")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para eliminar la entidad")

        elif action == "delete_attribute":
            # Obtener los parámetros necesarios
            attribute = parameters.get("attribute")
            entity = parameters.get("entity")

            if attribute and entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres eliminar el atributo {attribute} de la entidad {entity}?"
                respuesta = app_context.chatBoot.listen_and_transcribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.delete_attribute(entity, attribute)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se eliminará el atributo")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para eliminar el atributo")
        elif action == "update_collection":
            collection = Collection()
            collection.refreshCollection()
        else:
            # Caso para acciones desconocidas
            app_context.chatBoot.speak("Lo siento, no te he entendido")
            log_warning("Acción desconocida: " + action)  # Para depuración

