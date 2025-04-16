
class AppContext:
    def __init__(self):
        from emociones.backend.database.databaseHandler import DatabaseHandler
        from emociones.UI.chatbot import ChatBot
        self.chatBoot = ChatBot()
        self.dbHandler = DatabaseHandler(self.chatBoot)

app_context = AppContext()