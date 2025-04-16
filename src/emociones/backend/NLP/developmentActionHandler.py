from emociones.globals.globalVars import app_context
from emociones.backend.NLP.chatbotInterpreter import ChatbotInterpreter
from emociones.backend.NLP.interpreterTermsConfig import development_terms_to_actions
from emociones.backend.collection import Collection
from emociones.utils.log import logInfo, logWarning

class DevelopmentActionHandler:
    def __init__(self):
        self.interpreter = ChatbotInterpreter()
        self.terms_to_actions = development_terms_to_actions

    def handleText(self, text):
        # Interpretar el texto
        interpretation = self.interpreter.interpret(text, self.terms_to_actions)
        logInfo(f"Interpretación obtenida: {interpretation}")  # Para depuración

        # Extraer la acción y los parámetros
        action = interpretation["action"]
        parameters = interpretation["parameters"]

        if action == "createEntity":
            # Obtener los parámetros necesarios
            entity = parameters.get("entity")
            if entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres crear la entidad {entity}?"
                respuesta = app_context.chatBoot.listenAndTranscribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.createEntity(entity)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se creará la entidad")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para crear la entidad")

        elif action == "createAttribute":
            # Obtener los parámetros necesarios
            attribute = parameters.get("attribute")
            entity = parameters.get("entity")

            if attribute and entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres crear el atributo {attribute} para la entidad {entity}?"
                respuesta = app_context.chatBoot.listenAndTranscribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.createAttribute(entity, attribute)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se creará el atributo")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para crear el atributo")

        elif action == "deleteEntity":
            # Obtener los parámetros necesarios
            entity = parameters.get("entity")
            if entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres eliminar la entidad {entity}?"
                respuesta = app_context.chatBoot.listenAndTranscribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.deleteEntity(entity)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se eliminará la entidad")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para eliminar la entidad")

        elif action == "deleteAttribute":
            # Obtener los parámetros necesarios
            attribute = parameters.get("attribute")
            entity = parameters.get("entity")

            if attribute and entity:
                # Preguntar confirmación al usuario
                pregunta = f"¿Quieres eliminar el atributo {attribute} de la entidad {entity}?"
                respuesta = app_context.chatBoot.listenAndTranscribe(pregunta)

                if "si" in respuesta.lower():
                    app_context.dbHandler.deleteAttribute(entity, attribute)
                else:
                    app_context.chatBoot.speak("De acuerdo, no se eliminará el atributo")
            else:
                app_context.chatBoot.speak("No he entendido bien la información para eliminar el atributo")
        else:
            # Caso para acciones desconocidas
            app_context.chatBoot.speak("Lo siento, te he entendido mal o no puedo realizar esa acción")
            logWarning(f"Acción desconocida{action}")  # Para depuración

