from emociones.globals.globalVars import app_context
from emociones.IA.chatbotInterpreter import ChatbotInterpreter
from emociones.IA.interpreterTermsConfig import user_terms_to_actions
from emociones.backend.collection import Collection
from emociones.utils.log import log_info, log_warning

class UserActionHandler:
    def __init__(self):
        self.interpreter = ChatbotInterpreter()
        self.terms_to_actions = user_terms_to_actions

    def handle_text(self, text):
        # Interpretar el texto
        interpretation = self.interpreter.interpret(text, self.terms_to_actions)
        log_info(f"Interpretación obtenida: {interpretation}")  # Para depuración

        # Extraer la acción y los parámetros
        action = interpretation["action"]
        parameters = interpretation["parameters"]

        if action == "update_collection":
            collection = Collection()
            collection.refreshCollection()
        else:
            # Caso para acciones desconocidas
            app_context.chatBoot.speak("Lo siento, te he entendido mal o no puedo realizar esa acción")
            log_warning(f"Acción desconocida{action}")  # Para depuración

