import os
import mimetypes
from PyQt5.QtWidgets import QScrollArea, QLabel, QGridLayout, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt, QSize
from emociones.constants import (MAX_IMAGE_WIDTH, SIDE_MARGIN,SCROLLBAR_WIDTH, IMAGE, VIDEO)
from emociones.preferences import preferences
from emociones.utils.fileUtil import getFileDescription, isValidFile, generateGifFromMovie
from emociones.utils.log import logInfo, logError, logWarning
from emociones.backend.collection import Collection
from emociones.globals.globalVars import app_context


class Gallery:
    def __init__(self, content_layout):
        self.content_layout = content_layout
        self.scroll_area = None
        self.gallery_layout = None
        self.current_image_widgets = []

    def openFolderDialog(self):
        collection = Collection()
        # Abre un diálogo para seleccionar una carpeta
        folder_path = QFileDialog.getExistingDirectory(None, "Seleccionar carpeta de imágenes", preferences["gallery"]["galleryPath"])
        if folder_path:
            # Limpia el contenido actual
            self.clearContent()

            collectedCollection = collection.getCollectionFromFolder(folder_path)
            app_context.chatBoot.speak("Preparando galería")

            # Procesa las imágenes si se encontraron
            if collectedCollection:
                self.createGallery()
                self.addFilesToGallery(collectedCollection)
            else:
                logWarning("No se encontraron imágenes en la carpeta seleccionada.")
            app_context.chatBoot.speak("Disfrute de la galería")

    def clearContent(self):
        # Limpia los widgets actuales en el área de contenido
        if self.content_layout:
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.current_image_widgets = []  # Limpia la lista de widgets de imágenes

    
    def getFilePaths(self, folder_path):
        result = []

        # Listar solo los archivos en el directorio actual
        for file in os.listdir(folder_path):
            # Obtener la ruta completa del archivo
            file_path = os.path.join(folder_path, file)
            valid_file = isValidFile(file_path)
            if valid_file and valid_file[0]:
                # Agregar el archivo a la lista de resultados
                result.append(file_path)
            else:
                logWarning(f"El archivo {file_path} no es una imagen o un video válido.")
                continue

        return result
    
    def createGallery(self):
        app_context.chatBoot.speak("Abriendo galería")
        # Crea el área de desplazamiento para la galería
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        gallery_widget = QWidget()
        gallery_widget.setMinimumWidth(MAX_IMAGE_WIDTH + (2*SIDE_MARGIN) + SCROLLBAR_WIDTH)

        self.gallery_layout = QGridLayout(gallery_widget)

        self.scroll_area.setWidget(gallery_widget)
        self.content_layout.addWidget(self.scroll_area)
        app_context.chatBoot.speak("Galería abierta")

    def addFilesToGallery(self, file_paths):
        app_context.chatBoot.speak("Añadiendo imágenes a la galería")
        # Agrega las imágenes o GIFs seleccionados a la galería
        for file_path in file_paths:
            try:
                # Determinar el tipo MIME del archivo
                file_type, _ = mimetypes.guess_type(file_path)
                valid_file = isValidFile(file_path)
                if (valid_file is None):
                    logWarning(f"El archivo {file_path} no es una imagen o un video válido.")
                    continue
                # Crear un QLabel para el GIF
                label = QLabel()
                label.setToolTip(getFileDescription(file_path))
                
                # Verificar si es un GIF animado
                if valid_file[1] == VIDEO:
                    tempGif = generateGifFromMovie(file_path)
                    # Cargar el GIF en un QMovie y asignarlo al QLabel
                    movie = QMovie(tempGif)
                    if not movie.isValid():
                        logWarning(f"No se pudo cargar el GIF {tempGif}")
                        continue
                    original_size = movie.scaledSize()
                    scaled_height = int(MAX_IMAGE_WIDTH * original_size.height() / original_size.width())
                    movie.setScaledSize(QSize(MAX_IMAGE_WIDTH, scaled_height))

                    label.setMovie(movie)
                    movie.start()  # Iniciar la animación del GIF

                    # Almacenar el QLabel del GIF
                    self.current_image_widgets.append(label)

                # Verificar si es una imagen (no GIF)
                elif valid_file[1] == IMAGE:
                    pixmap = QPixmap(file_path)
                    if pixmap.isNull():
                        logWarning(f"No se pudo cargar la imagen {file_path}")
                        continue

                    # Escalar la imagen
                    scaled_height = int(MAX_IMAGE_WIDTH * pixmap.height() / pixmap.width())
                    scaled_pixmap = pixmap.scaled(MAX_IMAGE_WIDTH, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    label.setPixmap(scaled_pixmap)

                    # Almacenar el QLabel de la imagen
                    self.current_image_widgets.append(label)

                else:
                    logWarning(f"Archivo no soportado: {file_path}")
            except Exception as e:
                logError(f"Al cargar el archivo {file_path}: {e}")
            self.showGallery()

    def showGallery(self):
        # Intentar obtener el ancho del content_layout desde el widget padre
        parent_widget = self.content_layout.parentWidget()
        layout_width = parent_widget.geometry().width() if parent_widget else self.content_layout.geometry().width()

        if layout_width <= 0:  # Si el ancho no es válido
            layout_width = self.scroll_area.width()  # Usar scroll_area como respaldo
        
        # Determinar el ancho disponible considerando el espacio de content_layout o scroll_area
        layout_width = max((layout_width if layout_width > 0 else self.scroll_area.width()) - (2 * SIDE_MARGIN) - SCROLLBAR_WIDTH,MAX_IMAGE_WIDTH)
        # Calcula cuántas imágenes caben en la primera fila sin desbordar horizontalmente
        images_per_row = max(1, layout_width // (MAX_IMAGE_WIDTH + (2*SIDE_MARGIN)))

        # Ajusta el tamaño de cada imagen teniendo en cuenta el espaciamiento
        total_spacing = max((images_per_row - 1) * SIDE_MARGIN, 0)  # Espaciado entre imágenes, evitando negativos
        adjusted_image_width = (layout_width - total_spacing) // images_per_row

        # Configura los márgenes y el espaciado del diseño
        self.gallery_layout.setContentsMargins(SIDE_MARGIN, 0, SIDE_MARGIN, SIDE_MARGIN)
        self.gallery_layout.setHorizontalSpacing(SIDE_MARGIN)
        self.gallery_layout.setVerticalSpacing(SIDE_MARGIN)

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
            self.showGallery()
        super().resizeEvent(event)