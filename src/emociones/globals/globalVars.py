
class AppContext:
    def __init__(self):
        from emociones.backend.database.databaseHandler import DatabaseHandler
        from emociones.UI.chatbot import ChatBot
        from emociones.utils.log import logInfo
        logInfo("Iniciando Contexto")
        self.chatBoot = ChatBot()
        self.dbHandler = DatabaseHandler(self.chatBoot)
        logInfo("Contexto Iniciado")

app_context = AppContext()