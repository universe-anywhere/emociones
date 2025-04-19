import os
import sys
class AppContext:
    def __init__(self):
        from emociones.backend.database.databaseHandler import DatabaseHandler
        from emociones.UI.chatbot import ChatBot
        from emociones.utils.log import logInfo
        from emociones.utils.io import getBasePath
        logInfo("Iniciando Contexto")
        yolov5_path = os.path.join(getBasePath(), "yolov5")
        sys.path.append(yolov5_path)
        self.chatBoot = ChatBot()
        self.dbHandler = DatabaseHandler(self.chatBoot)
        self.workingCollectionItems = None
        logInfo("Contexto Iniciado")

app_context = AppContext()