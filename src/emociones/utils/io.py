import os
import sys

def get_base_path():
    """
    Obtiene la ruta base del proyecto dependiendo del entorno:
    - Si se ejecuta en un ejecutable empaquetado con PyInstaller, utiliza sys._MEIPASS.
    - Si está en desarrollo, utiliza el directorio actual de ejecución.
    
    Returns:
        str: Ruta base del proyecto.
    """
    if hasattr(sys, '_MEIPASS'):
        # En el entorno PyInstaller, la base será sys._MEIPASS
        base_path = sys._MEIPASS
        if not base_path.endswith("emociones"):
            base_path = os.path.join(base_path, "emociones")

        print(f"Mostrando archivos en: {base_path}")

        for root, dirs, files in os.walk(base_path):
            print(f"\nDirectorio: {root}")
            for dir_name in dirs:
                print(f"  [Carpeta] {dir_name}")
            for file_name in files:
                print(f"  [Archivo] {file_name}")

    else:
        # En desarrollo, utiliza la ruta del directorio actual
        base_path = os.getcwd()
        if not base_path.endswith("src"):
            base_path = os.path.join(base_path, "src")
        if not base_path.endswith("emociones"):
            base_path = os.path.join(base_path, "emociones")
        
    return base_path