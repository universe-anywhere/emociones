import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QPushButton, QWidget, 
)
from emociones.UI.gallery import Gallery
from emociones.UI.chatbot import ChatBot
from emociones.UI.settings import Settings

from emociones.constants import (MAX_IMAGE_WIDTH, SIDE_MARGIN, SCROLLBAR_WIDTH, WIDGET_ADDED_WIDTH)

class EmocionesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.buttons = {
            "Hablar con el Chatbot": self.open_chatbot_dialog,
            "Gestionar Galería": self.manage_gallery,
            "Ajustes": self.open_settings,  # Otro ejemplo
        }

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
        self.main_layout.addLayout(self.content_layout)

    def open_chatbot_dialog(self):
        # Usar una variable local para instanciar ChatBot
        chatBot_instance = getattr(self, "_chatBoot_instance", None)  # Comprobar si ya existe la instancia
        if not chatBot_instance:
            chatBot_instance = ChatBot()
            setattr(self, "_chatBoot_instance", chatBot_instance)  # Guardar la instancia como atributo dinámico

        chatBot_instance.open_chatbot_dialog()  # Abrir el diálogo del chatbot    


    def manage_gallery(self):
        # Usar una variable local para instanciar Gallery
        gallery_instance = getattr(self, "_gallery_instance", None)  # Comprobar si ya existe la instancia
        if not gallery_instance:
            gallery_instance = Gallery(self.content_layout)
            setattr(self, "_gallery_instance", gallery_instance)  # Guardar la instancia como atributo dinámico
        gallery_instance.open_folder_dialog()

    def resizeEvent(self, event):
        # Verificar si existe _gallery_instance y ajustarla al redimensionar
        gallery_instance = getattr(self, "_gallery_instance", None)  # Obtener la instancia dinámica
        if gallery_instance and hasattr(gallery_instance, 'gallery_layout'):
            gallery_instance.show_gallery()  # Ajustar la galería
        super().resizeEvent(event)

    def open_settings(self):
        settings_instance = Settings(self)
        settings_instance.open_settings()

def main():
    import sys
    app = QApplication(sys.argv)
    window = EmocionesApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()