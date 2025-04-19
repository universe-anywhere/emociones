import os
import cv2
import tempfile
from PyQt5.QtWidgets import QScrollArea, QGridLayout, QWidget, QFileDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QMovie, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QSize, QRectF
from PIL import Image, ImageDraw
from emociones.constants import (MAX_IMAGE_WIDTH, SIDE_MARGIN,SCROLLBAR_WIDTH, IMAGE, VIDEO, GIF_MAX_FRAMES)
from emociones.preferences import preferences
from emociones.utils.fileUtil import getFileDescription, isValidFile, fileType
from emociones.utils.log import logInfo, logError, logWarning
from emociones.backend.collection import Collection
from emociones.globals.globalVars import app_context
from emociones.UI.hoverQlabel import HoverQlabel

class Gallery:
    def __init__(self, content_layout):
        logInfo("Iniciando Gallery")
        self.content_layout = content_layout
        self.scroll_area = None
        self.gallery_layout = None
        self.current_image_widgets = []
        logInfo("Gallery iniciada")

    def roundPixmap(self, file_path):
        radius = 10  # Radio de esquinas redondeadas

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            logWarning(f"No se pudo cargar la imagen {file_path}")
            return None

        # Escalar la imagen
        scaled_height = int(MAX_IMAGE_WIDTH * pixmap.height() / pixmap.width())
        pixmap = pixmap.scaled(MAX_IMAGE_WIDTH, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

       # Obtener el ancho y alto del pixmap
        width = pixmap.width()
        height = pixmap.height()

        # Crear un nuevo lienzo transparente con las dimensiones separadas
        rounded = QPixmap(width - 2 * radius, height - 2 * radius)
        rounded.fill(Qt.transparent)

        # Configurar el pintor y crear el path redondeado
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(0, 0, width - 2 * radius, height - 2 * radius)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # Establecer el clip (máscara) y luego pintar el pixmap
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)

        painter.end()
        return rounded

    def generateGifFromMovie(self, video_path):

        try:
            # Abrir el vídeo con OpenCV
            video = cv2.VideoCapture(video_path)

            if not video.isOpened():
                logWarning(f"No se pudo abrir el archivo de video {video_path}")
                return None

            frames = []
            gif_path = os.path.join(tempfile.gettempdir(), f"{os.path.splitext(os.path.basename(video_path))[0]}.gif")

            # Obtener total de fotogramas en el vídeo
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            step = max(1, total_frames // GIF_MAX_FRAMES)

            for i in range(GIF_MAX_FRAMES):  # Capturar hasta GIF_MAX_FRAMES fotogramas espaciados
                video.set(cv2.CAP_PROP_POS_FRAMES, i * step)
                success, frame = video.read()

                if not success:
                    logWarning(f"No se pudo leer el fotograma {i} del video {video_path}")
                    break

                # Convertir el fotograma de BGR (OpenCV) a RGB (Pillow)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Crear una imagen PIL desde el fotograma
                pil_image = Image.fromarray(frame_rgb)

                # Redondear las esquinas del fotograma
                rounded_frame = self.addRoundedCornersToImage(pil_image)
                frames.append(rounded_frame)

            # Generar el GIF animado con un intervalo de 0.5 segundos entre fotogramas
            if frames:
                frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=500,  # 500 milisegundos = 0.5 segundos por fotograma
                    loop=0  # Número de repeticiones (0 = infinito)
                )
                logInfo(f"GIF generado correctamente en: {gif_path}")
                return gif_path
            else:
                logWarning(f"No se pudieron obtener suficientes fotogramas para generar el GIF.")
                return None
        finally:
            video.release()

    def addRoundedCornersToImage(self, image):
        """
        Redondea las esquinas de una imagen PIL.
        """
        radius = 10
        # Crear una máscara para redondear las esquinas
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=255)

        # Aplicar la máscara a la imagen original
        rounded_image = Image.new("RGB", image.size)
        rounded_image.paste(image, (0, 0), mask)
        return rounded_image
    
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

    def previewGallery(self):
        collectionItems = app_context.workingCollectionItems
        if collectionItems is None:
            app_context.chatBoot.speak("No estás trabajando con ninguna colección")
            logError("No hay resultados para generar la galería.")
            return

        app_context.chatBoot.speak(f"Preparando vista previa de galería para la colección de {len(collectionItems)} elementos")
        # Limpia el contenido actual
        self.clearContent()

        # Procesa las imágenes si se encontraron
        self.createGallery()
        self.addFilesToGallery(collectionItems)

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
            if valid_file:
                # Agregar el archivo a la lista de resultados
                result.append(file_path)
            else:
                logWarning(f"El archivo {file_path} no es una imagen o un video válido.")
                continue

        return result
        
    def createGallery(self):
        app_context.chatBoot.speak("Abriendo galería")

        # Crear área de desplazamiento para la galería
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        gallery_widget = QWidget()
        gallery_widget.setMinimumWidth(MAX_IMAGE_WIDTH + (2 * SIDE_MARGIN) + SCROLLBAR_WIDTH)

        # Configurar layout con márgenes y espaciado
        self.gallery_layout = QGridLayout(gallery_widget)
        self.gallery_layout.setContentsMargins(SIDE_MARGIN, SIDE_MARGIN, SIDE_MARGIN, SIDE_MARGIN)
        self.gallery_layout.setHorizontalSpacing(SIDE_MARGIN)
        self.gallery_layout.setVerticalSpacing(SIDE_MARGIN)

        self.scroll_area.setWidget(gallery_widget)
        self.content_layout.addWidget(self.scroll_area)
        
    def addFilesToGallery(self, file_paths):
        for file_path in file_paths:
            try:
                # Determinar el tipo MIME del archivo
                file_type = fileType(file_path)
                if file_type not in (IMAGE, VIDEO):
                    logWarning(f"El archivo {file_path} no es una imagen o un video válido.")
                    continue

                # Crear una instancia de HoverQlabel
                label = HoverQlabel()

                if file_type == VIDEO:
                    tempGif = self.generateGifFromMovie(file_path)
                    if not tempGif:
                        logWarning(f"No se pudo generar el GIF para el video {file_path}")
                        continue

                    movie = QMovie(tempGif)
                    if movie.isValid():
                        movie.setScaledSize(QSize(MAX_IMAGE_WIDTH, MAX_IMAGE_WIDTH))  
                        label.image_label.setMovie(movie)  # Asignar el QMovie al QLabel interno
                        movie.start()
                        self.current_image_widgets.append(label)

                elif file_type == IMAGE:
                    rounded_pixmap = self.roundPixmap(file_path)
                    if rounded_pixmap is not None:
                        label.setImage(rounded_pixmap)  # Establecer la imagen en el QLabel interno
                        self.current_image_widgets.append(label)

                # Asegurar que el widget tenga un tamaño definido (opcional)
                label.setMinimumSize(120, 120)

                # Agregar el HoverQlabel al diseño de la galería
                self.gallery_layout.addWidget(label)

            except Exception as e:
                logError(f"Error al procesar el archivo {file_path}: {e}")
            self.showGallery()

    def showGallery(self):
        if self.gallery_layout is None:
            return

        # Obtener el ancho del contenedor (content_layout o scroll_area)
        parent_widget = self.content_layout.parentWidget()
        layout_width = parent_widget.geometry().width() if parent_widget else self.content_layout.geometry().width()

        if layout_width <= 0:  # Usar scroll_area como respaldo si el ancho no es válido
            layout_width = self.scroll_area.width()

        # Ajustar el ancho para considerar márgenes y scrollbar
        layout_width = max(
            (layout_width if layout_width > 0 else self.scroll_area.width()) - (2 * SIDE_MARGIN) - SCROLLBAR_WIDTH,
            MAX_IMAGE_WIDTH
        )

        # Calcular cuántos elementos caben por fila
        images_per_row = max(1, layout_width // (MAX_IMAGE_WIDTH + (2 * SIDE_MARGIN)))
        total_spacing = max((images_per_row - 1) * SIDE_MARGIN, 0)  # Espaciado horizontal total
        adjusted_image_width = (layout_width - total_spacing) // images_per_row

        # Configurar márgenes y espaciado del layout
        self.gallery_layout.setContentsMargins(SIDE_MARGIN, SIDE_MARGIN, SIDE_MARGIN, SIDE_MARGIN)
        self.gallery_layout.setHorizontalSpacing(SIDE_MARGIN)
        self.gallery_layout.setVerticalSpacing(SIDE_MARGIN)

        # Redimensionar y organizar los widgets dentro del layout
        for index, widget in enumerate(self.current_image_widgets):
            row = index // images_per_row
            col = index % images_per_row

            # Expandir cada widget para que llene su celda
            widget.setFixedSize(adjusted_image_width, adjusted_image_width)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Agregar widget con alineación centrada
            self.gallery_layout.addWidget(widget, row, col, alignment=Qt.AlignCenter)

    def resizeEvent(self, event):
        # Ajusta el diseño de las imágenes existentes al redimensionar la ventana
        if self.gallery_layout is None:
            return
        self.showGallery()
        super().resizeEvent(event)
