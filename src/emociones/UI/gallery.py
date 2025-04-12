import os
from PyQt5.QtWidgets import QScrollArea, QLabel, QGridLayout, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from constants import (MAX_IMAGE_WIDTH, SIDE_MARGIN,SCROLLBAR_WIDTH)


class Gallery:
    def __init__(self, content_layout):
        self.content_layout = content_layout
        self.scroll_area = None
        self.gallery_layout = None
        self.current_image_widgets = []

    def open_folder_dialog(self):
        # Abre un diálogo para seleccionar una carpeta
        folder_path = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta de imágenes")
        if folder_path:
            # Limpia el contenido actual
            self.clear_content()

            # Busca las imágenes en la carpeta seleccionada
            image_paths = self.get_image_paths(folder_path)
            if image_paths:
                self.create_gallery()
                self.add_images_to_gallery(image_paths)
            else:
                print("No se encontraron imágenes en la carpeta seleccionada.")

    def clear_content(self):
        # Limpia los widgets actuales en el área de contenido
        if self.content_layout:
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.current_image_widgets = []  # Limpia la lista de widgets de imágenes

    def get_image_paths(self, folder_path):
        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        result = []

        try:
            for root, _, files in os.walk(folder_path):  # Recorre carpetas y subcarpetas
                for file_name in files:
                    if file_name.lower().endswith(supported_extensions):
                        result.append(os.path.join(root, file_name))  # Construye la ruta completa
            return result
        except FileNotFoundError:
            print(f"La carpeta '{folder_path}' no existe.")
            return []
        except PermissionError:
            print(f"No se tienen permisos para acceder a la carpeta '{folder_path}'.")
            return []

    def create_gallery(self):
        # Crea el área de desplazamiento para la galería
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        gallery_widget = QWidget()
        gallery_widget.setMinimumWidth(MAX_IMAGE_WIDTH + (2*SIDE_MARGIN) + SCROLLBAR_WIDTH)

        self.gallery_layout = QGridLayout(gallery_widget)

        self.scroll_area.setWidget(gallery_widget)
        self.content_layout.addWidget(self.scroll_area)

    def add_images_to_gallery(self, image_paths):
        # Agrega las imágenes seleccionadas a la galería
        for image_path in image_paths:
            try:
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    print(f"Error: No se pudo cargar la imagen {image_path}")
                    continue

                # Escalar la imagen
                scaled_height = int(MAX_IMAGE_WIDTH * pixmap.height() / pixmap.width())
                scaled_pixmap = pixmap.scaled(MAX_IMAGE_WIDTH, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Crear un QLabel para la imagen
                label = QLabel()
                label.setPixmap(scaled_pixmap)

                # Almacena el widget de la imagen
                self.current_image_widgets.append(label)
            except Exception as e:
                print(f"Error al cargar la imagen {image_path}: {e}")

        self.show_gallery()

    def show_gallery(self):
        # Determinar el ancho disponible considerando el espacio de content_layout o scroll_area
        layout_width = self.content_layout.geometry().width()
        window_width = max((layout_width if layout_width > 0 else self.scroll_area.width()) - (2 * SIDE_MARGIN) - SCROLLBAR_WIDTH, MAX_IMAGE_WIDTH)

        # Calcula cuántas imágenes caben en la primera fila sin desbordar horizontalmente
        images_per_row = max(1, window_width // MAX_IMAGE_WIDTH)

        # Ajusta el tamaño de cada imagen teniendo en cuenta el espaciamiento
        total_spacing = max((images_per_row - 1) * SIDE_MARGIN, 0)  # Espaciado entre imágenes, evitando negativos
        adjusted_image_width = (window_width - total_spacing) // images_per_row

        # Configura los márgenes y el espaciado del diseño
        self.gallery_layout.setContentsMargins(SIDE_MARGIN, 0, SIDE_MARGIN, 0)
        self.gallery_layout.setHorizontalSpacing(10)
        self.gallery_layout.setVerticalSpacing(10)

        # Centra las filas de la galería en el contenedor
        self.gallery_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Reorganiza los widgets existentes y alinea los widgets de fotos a la izquierda
        for index, widget in enumerate(self.current_image_widgets):
            row = index // images_per_row
            col = index % images_per_row
            widget.setFixedSize(adjusted_image_width, adjusted_image_width)

            # Agregar el widget al layout con alineación izquierda
            self.gallery_layout.addWidget(widget, row, col, alignment=Qt.AlignLeft)

    def resizeEvent(self, event):
        # Ajusta el diseño de las imágenes existentes al redimensionar la ventana
        if hasattr(self, 'gallery_layout'):
            self.show_gallery()
        super().resizeEvent(event)