import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QPushButton, QWidget, 
)
from emociones.UI.gallery import Gallery
from emociones.constants import (MAX_IMAGE_WIDTH, SIDE_MARGIN, SCROLLBAR_WIDTH, WIDGET_ADDED_WIDTH)

class EmocionesApp(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # Botón para gestionar la galería
        self.menu_button = QPushButton("Gestionar")
        self.button_layout.addWidget(self.menu_button)

        # Sección inferior: contenido dinámico
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Conectar el botón para instanciar Gallery y abrir el diálogo
        self.menu_button.clicked.connect(self.manage_gallery)

        # Variable para almacenar la instancia de Gallery
        self.gallery = None

    def manage_gallery(self):
        # Instanciar Gallery solo cuando se presione el botón
        if not self.gallery:
            self.gallery = Gallery(self.content_layout)
        self.gallery.open_folder_dialog()

    def resizeEvent(self, event):
        # Ajusta la galería al redimensionar la ventana
        if self.gallery and hasattr(self.gallery, 'gallery_layout'):
            self.gallery.show_gallery()
        super().resizeEvent(event)

def main():
    import sys
    app = QApplication(sys.argv)
    window = EmocionesApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()