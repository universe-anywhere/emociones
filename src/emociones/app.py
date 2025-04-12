import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QScrollArea, 
    QLabel, QPushButton, QGridLayout, QWidget, QFileDialog,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class EmocionesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emociones (Fotos y Videos)")
        self.setGeometry(100, 100, 800, 600)

        # Contenedor principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Menú desplegable (botón para gestionar)
        self.menu_button = QPushButton("Gestionar")
        self.menu_button.clicked.connect(self.open_folder_dialog)
        self.main_layout.addWidget(self.menu_button)

        self.max_image_width = 150

    def open_folder_dialog(self):
        # Abre un diálogo para seleccionar una carpeta
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de imágenes")
        if folder_path:
            # Limpia los elementos actuales de la galería si ya existen
            self.clear_gallery()

            # Crear los elementos relacionados con la galería
            self.create_gallery()

            # Busca las imágenes en la carpeta seleccionada
            image_paths = self.get_image_paths(folder_path)
            if image_paths:  # Si hay imágenes válidas
                self.add_images_to_gallery(image_paths)
            else:
                print("No se encontraron imágenes en la carpeta seleccionada.")

    def clear_gallery(self):
        # Elimina los widgets e imágenes actuales en la galería
        if hasattr(self, 'gallery_layout'):
            while self.gallery_layout.count():  # Elimina todos los widgets en el layout
                item = self.gallery_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def create_gallery(self):
        # Crea el contenedor para la galería
        self.gallery_layout = QGridLayout()
        self.gallery_widget = QWidget()
        self.gallery_widget.setLayout(self.gallery_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.gallery_widget)
        self.main_layout.addWidget(self.scroll_area)

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

    def show_gallery(self):
        # Define el ancho máximo inicial de cada imagen
        side_margin = 10  # Márgenes izquierdo y derecho iguales

        # Reserva espacio para la barra de desplazamiento vertical (16 px estándar)
        scrollbar_width = 35  # Siempre reservado, independientemente de su visibilidad

        # Obtiene el ancho disponible en el área de la galería considerando la barra de scroll
        window_width = self.scroll_area.viewport().width() - (2 * side_margin) - scrollbar_width

        # Calcula cuántas imágenes caben en la primera fila sin desbordar horizontalmente
        images_per_row = max(1, window_width // self.max_image_width)

        # Calcula el ancho de las imágenes en la primera fila y lo usa para todas las filas
        total_spacing = (images_per_row - 1) * 10  # Espaciado entre imágenes
        adjusted_image_width = (window_width - total_spacing) // images_per_row  # Valor fijo para todas las filas

        # Configura los márgenes y espaciados del layout
        self.gallery_layout.setContentsMargins(side_margin, 0, side_margin, 0)
        self.gallery_layout.setHorizontalSpacing(10)
        self.gallery_layout.setVerticalSpacing(10)

        # Reorganiza los widgets existentes sin volver a cargarlos
        for index, widget in enumerate(self.current_image_widgets):
            row = index // images_per_row
            col = index % images_per_row
            widget.setFixedSize(adjusted_image_width, adjusted_image_width)  # Ajustar el tamaño
            self.gallery_layout.addWidget(widget, row, col)

    def resizeEvent(self, event):
        # Ajusta el diseño de las imágenes existentes al redimensionar la ventana
        if hasattr(self, 'gallery_layout'):
            self.show_gallery()
        super().resizeEvent(event)

    def add_images_to_gallery(self, image_paths):
        # Almacenar las rutas de las imágenes cargadas
        self.current_image_paths = image_paths
        self.current_image_widgets = []

        for image_path in image_paths:
            try:
                # Cargar la imagen completa desde el archivo
                pixmap = QPixmap(image_path)
                
                # Validar que la imagen se haya cargado correctamente
                if pixmap.isNull():
                    print(f"Error: No se pudo cargar la imagen {image_path}")
                    continue

                scaled_height = int(self.max_image_width * pixmap.height() / pixmap.width())

                # Escalar el pixmap usando Qt.KeepAspectRatio
                scaled_pixmap = pixmap.scaled(self.max_image_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Crear el QLabel para mostrar la imagen
                label = QLabel()
                label.setPixmap(scaled_pixmap)

                # Almacenar el widget de la imagen
                self.current_image_widgets.append(label)
            except Exception as e:
                print(f"Error al cargar la imagen {image_path}: {e}")

        # Mostrar la galería por primera vez
        self.show_gallery()


def main():
    import sys
    app = QApplication(sys.argv)
    window = EmocionesApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()