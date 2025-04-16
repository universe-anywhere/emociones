import hashlib
import os
import tempfile
import mimetypes
import cv2
from PIL import Image
from emociones.constants import (IMAGE, VIDEO, GIF_MAX_FRAMES)
from emociones.utils.log import logInfo, logError, logWarning

def calculateHash(filePath):
    """
    Calcula la firma hash SHA-256 de un archivo.

    Args:
        filePath (str): Ruta completa del archivo a procesar.

    Returns:
        str: Hash SHA-256 en formato hexadecimal.
    """
    try:
        # Crear un objeto hash
        sha256_hash = hashlib.sha256()

        # Abrir el archivo en modo binario
        logInfo(f"Calculando hash para el archivo: {filePath}")
        with open(filePath, "rb") as file:
            # Leer el archivo en bloques para evitar problemas de memoria con archivos grandes
            for bloque in iter(lambda: file.read(4096), b""):
                sha256_hash.update(bloque)

        logInfo(f"Firma hash calculada: {sha256_hash.hexdigest()}")
        # Devolver el hash en formato hexadecimal
        return sha256_hash.hexdigest()

    except FileNotFoundError:
        logError(f"El archivo '{filePath}' no fue encontrado.")
        return None
    except Exception as e:
        logError(f"Al calcular el hash: {e}")
        return None

def getFileName(file_path):
    """
    Obtiene el nombre del archivo sin la extensión.

    Args:
        file_path (str): Ruta completa del archivo.

    Returns:
        str: Nombre del archivo sin la extensión.
    """
    # Obtener el nombre del archivo completo
    file_name_with_extension = os.path.basename(file_path)
    
    # Separar el nombre del archivo y la extensión
    file_name, _ = os.path.splitext(file_name_with_extension)

    return file_name

def getFileDescription(file_path):    
   # Obtener el nombre del archivo completo
    file_name_with_extension = os.path.basename(file_path)
    
    # Separar el nombre del archivo y la extensión
    file_name, _ = os.path.splitext(file_name_with_extension)

    return file_name

def generateGifFromMovie(video_path):
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

        # Elegir GIF_MAX_FRAMES fotogramas distribuidos uniformemente
        step = max(1, total_frames // GIF_MAX_FRAMES)  # Distribuir los fotogramas a lo largo del vídeo

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
            frames.append(pil_image)

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

def fileType(file_path):
   # Verifica si el archivo es una imagen o un video
    file_type, _ = mimetypes.guess_type(file_path)

    logInfo(f"Tipo de archivo: {file_type} - Archivo: {file_path}")
    if file_type and file_type.startswith(IMAGE):
        return  IMAGE
    elif file_type and file_type.startswith(VIDEO):
        return  VIDEO
    return None

def isValidFile(file_path):
    # Verificar si es un archivo (y no una carpeta)
    if not os.path.isfile(file_path):
        return False
    return True
    

 