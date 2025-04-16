from emociones.globals.globalVars import app_context
from emociones.backend.NLP.chatbotInterpreter import ChatbotInterpreter
from emociones.backend.NLP.interpreterTermsConfig import user_terms_to_actions
from emociones.backend.collection import Collection
from emociones.utils.log import logInfo, logWarning
from emociones.preferences import preferences

class UserActionHandler:
    def __init__(self, face_processor, collection):
        self.interpreter = ChatbotInterpreter()
        self.terms_to_actions = user_terms_to_actions
        self.face_processor = face_processor  # Instancia compartida de FaceProcessor
        self.collection = collection  # Instancia de Collection para actualizar la colección
    def handleText(self, text):
        # Interpretar el texto
        interpretation = self.interpreter.interpret(text, self.terms_to_actions)
        logInfo(f"Interpretación obtenida: {interpretation}")  # Para depuración

        # Extraer la acción y los parámetros
        action = interpretation["action"]

        if action == "update_collection":
            self.collection.refreshCollection()
        elif action == "face_recognition":
            # Usar la instancia compartida de FaceProcessor
            self.face_processor.processFiles(self.collection.getCollectionFromFolder(preferences["gallery"]["galleryPath"]))
        else:
            # Caso para acciones desconocidas
            app_context.chatBoot.speak("Lo siento, te he entendido mal o no puedo realizar esa acción")
            logWarning(f"Acción desconocida {action}")  # Para depuración