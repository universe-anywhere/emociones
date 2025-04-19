from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt

class HoverQlabel(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar layout interno
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 10)  # Márgenes alrededor de la imagen
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Crear QLabel para la imagen
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.layout.addWidget(self.image_label)

        # Configurar política de expansión
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Estilos y estado inicial
        self.original_style = "background-color: transparent;"
        self.hover_style = "background-color: #4FA8D1;"
        self.selected_style = "background-color: #4FA8D1;"
        self.selected = False

        self.updateStyle()

    def setImage(self, pixmap):
        self.image_label.setPixmap(pixmap)

    def enterEvent(self, event):
        if not self.selected:
            self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.selected:
            self.setStyleSheet(self.original_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.updateStyle()
        super().mousePressEvent(event)

    def updateStyle(self):
        if self.selected:
            self.setStyleSheet(self.selected_style)
        else:
            self.setStyleSheet(self.original_style)

            