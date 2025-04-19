import hashlib
import os
import mimetypes
from emociones.constants import (IMAGE, VIDEO)
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
    

 