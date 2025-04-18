import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QPushButton, QWidget, 
)
from emociones.globals.globalVars import app_context
from emociones.constants import (MAX_IMAGE_WIDTH, SIDE_MARGIN, SCROLLBAR_WIDTH, WIDGET_ADDED_WIDTH)
from emociones.UI.gallery import Gallery
from emociones.UI.settings import Settings
from emociones.backend.NLP.userActionHandler import UserActionHandler
from emociones.backend.NLP.developmentActionHandler import DevelopmentActionHandler
from emociones.backend.NLP.interpreterTermsConfig import development_terms_to_actions, user_terms_to_actions
from emociones.backend.FaceRecognition.faceProcessor import FaceProcessor
from emociones.backend.collection import Collection
from emociones.utils.log import logInfo
from emociones.preferences import preferences


class EmocionesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        app_context.chatBoot.speak("Bienvenido, le ruego un margen de 3 segundos cada vez que interactúe conmigo")  
        
        # Instancia de FaceProcessor
        self.face_processor = FaceProcessor()
        self.collection = Collection()
        # Instancia de UserActionHandler
        self.user_action_handler = UserActionHandler(self.face_processor,self.collection)
        
        self.buttons = {}
        if (preferences["config"]["developmentMode"]):
            self.developmentActionHandler = DevelopmentActionHandler()
            self.buttons["ChatBot Desarrolladores"] = lambda: self.openChatbotDialog(self.developmentActionHandler)

        self.buttons.update({
            "Hablar con el Chatbot": lambda: self.openChatbotDialog(self.user_action_handler),
            "Gestionar Galería": lambda: self.manageGallery(),
            "Ajustes": lambda: self.openSettings(),  # Otro ejemplo
        })

        self.setWindowTitle("Emociones (Fotos y Videos)")
        self.setGeometry(100, 100, 800, 600)

        # Contenedor principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.central_widget.setMinimumWidth(MAX_IMAGE_WIDTH + (2*SIDE_MARGIN) + SCROLLBAR_WIDTH + WIDGET_ADDED_WIDTH);
        # Diseño principal (vertical)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Sección superior: botones
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        for text, function in self.buttons.items():
            button = QPushButton(text)
            self.button_layout.addWidget(button)
            button.clicked.connect(function)

        # Sección inferior: contenido dinámico
        self.content_layout = QVBoxLayout()
        setattr(app_context, "_gallery_instance", Gallery(self.content_layout))  # Guardar la instancia como atributo dinámico
        self.main_layout.addLayout(self.content_layout)

    def openChatbotDialog(self, iaHandler):

        transcribed_text = app_context.chatBoot.openChatbotDialog()  # Abrir el diálogo del chatbot    
        logInfo("Texto transcrito: " + transcribed_text)  # Registrar el texto transcrito
        if (transcribed_text != ""):
            iaHandler.handleText(transcribed_text)  # Manejar la acción con ActionHandler

    def manageGallery(self):
        galleryInstance = getattr(app_context, "_gallery_instance", None)  # Comprobar si ya existe la instancia
        galleryInstance.openFolderDialog()

    def resizeEvent(self, event):
        # Verificar si existe _gallery_instance y ajustarla al redimensionar
        gallery_instance = getattr(app_context, "_gallery_instance", None)  # Obtener la instancia dinámica
        gallery_instance.showGallery()  # Ajustar la galería
        super().resizeEvent(event)

    def openSettings(self):
        settings_instance = Settings(self)
        settings_instance.openSettings()

    def closeEvent(self, event):
        """
        Sobrescribe el evento de cierre de la ventana para detener los hilos en ejecución.
        """
        logInfo("Deteniendo hilos antes de cerrar la aplicación.")
        #app_context.chatBoot.speak("Deteniendo procesos en ejcucion, te avisare cuando haya terminado")  
        
        if self.face_processor.isRunning:
            logInfo("Deteniendo el hilo de face_processor")
            self.face_processor.stopDetection()  # Detener el hilo de detección
        
        if self.collection.isRunning:
            logInfo("Deteniendo el hilo de collection")
            self.collection.stopDetection()  # Detener el hilo de detección
        
        #app_context.chatBoot.speak("Procesos detennidos, cerrando aplicación")  
        logInfo("Cerrando la aplicación.")
        
        event.accept()  # Permitir el cierre de la ventana

def main():
    import sys
    app = QApplication(sys.argv)
    window = EmocionesApp()
    window.show()
    sys.exit(app.exec_())

def __del__(self):
    pass

if __name__ == "__main__":
    main()