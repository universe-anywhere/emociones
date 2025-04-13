from emociones.database.databaseHandler import DatabaseHandler
from emociones.IA.chatbotInterpreter import ChatbotInterpreter

class ActionHandler:
    def __init__(self, chatBoot):
        self.db = DatabaseHandler()
        self.interpreter = ChatbotInterpreter()
        self.chatBootInstance = chatBoot  # Guardar la instancia de ChatBot
    def handle_text(self, text):
        interpretation = self.interpreter.interpret(text)
        print(f"Interpretación obtenida: {interpretation}")  # Depuración
        if interpretation["action"] == "create_entity":
            respuesta = self.chatBootInstance.listen_and_transcribe(f"¿Quieres crear la entidad {interpretation['name']}?")  # Reproducir la interpretación por los altavoces
            if ("sí" in respuesta.lower()):
                self.chatBootInstance.speak(f"Trabajando...")  
                self.db.create_entity(interpretation["name"]) 
                self.chatBootInstance.speak(f"Se ha creado la entidad {interpretation['name']}")  # Reproducir "No se creará la entidad" por los altavoces
            else:
                self.chatBootInstance.speak("De acuerdo, no se creará la entidad")  # Reproducir "No se creará la entidad" por los altavoces
        elif interpretation["action"] == "create_attribute":
            respuesta = self.chatBootInstance.listen_and_transcribe(f"¿Quieres crear la el atributo {interpretation['attribute_name']} para la entidad {interpretation['entity_name']}?")  # Reproducir la interpretación por los altavoces
            if ("sí" in respuesta.lower()):
                self.chatBootInstance.speak(f"Trabajando...")  
                self.db.create_attribute(interpretation["entity_name"], interpretation["attribute_name"])
                self.chatBootInstance.speak(f"Se ha creado el atributo {interpretation['attribute_name']} para la entidad {interpretation['entity_name']}")  # Reproducir "No se creará la entidad" por los altavoces
            else:
                self.chatBootInstance.speak("De acuerdo, no se creará el atributo")  # Reproducir "No se creará la entidad" por los altavoces
        else:
            self.chatBootInstance.speak(f"Lo siento no te he entendido correctamente")  # Reproducir "No se creará la entidad" por los altavoces
            print("Acción desconocida.")

    def close(self):
        self.db.close()
