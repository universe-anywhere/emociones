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
            app_context.dbHandler.createEntity(parameters)

        elif action == "createAttribute":
            app_context.dbHandler.createAttribute(parameters)

        elif action == "deleteEntity":
            app_context.dbHandler.deleteEntity(parameters)

        elif action == "deleteAttribute":
            app_context.dbHandler.deleteAttribute(parameters)
        else:
            # Caso para acciones desconocidas
            app_context.chatBoot.speak("Lo siento, te he entendido mal o no puedo realizar esa acción")
            logWarning(f"Acción desconocida{action}")  # Para depuración

