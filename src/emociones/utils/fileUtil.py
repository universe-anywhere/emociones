import hashlib

def calcular_hash(filePath):
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
        print(f"Calculando hash para el archivo: {filePath}")
        with open(filePath, "rb") as file:
            # Leer el archivo en bloques para evitar problemas de memoria con archivos grandes
            for bloque in iter(lambda: file.read(4096), b""):
                sha256_hash.update(bloque)

        print(f"Firma hash calculada: {sha256_hash.hexdigest()}")
        # Devolver el hash en formato hexadecimal
        return sha256_hash.hexdigest()

    except FileNotFoundError:
        print(f"Error: El archivo '{filePath}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al calcular el hash: {e}")
        return None