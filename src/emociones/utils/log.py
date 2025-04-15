import logging
import os
from emociones.preferences import preferences

# Crear carpeta de logs si no existe
os.makedirs(preferences["logs"]["log_path"], exist_ok=True)

# Ruta completa del archivo de log
log_file_path = os.path.join(preferences["logs"]["log_path"], preferences["logs"]["log_file"])

# Configurar el sistema de logging
logging.basicConfig(
    filename=log_file_path,  # Guardar logs en el archivo especificado
    level=getattr(logging, preferences["logs"]["log_level"].upper(), logging.ERROR),  # Establecer el nivel de log
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def logInfo(message):
    """Registra un mensaje de nivel INFO."""
    logging.info(message)

def logWarning(message):
    """Registra un mensaje de nivel WARNING."""
    logging.warning(message)

def logDebug(message):
    """Registra un mensaje de nivel DEBUG."""
    logging.debug(message)

def logError(message):
    """Registra un mensaje de nivel ERROR."""
    logging.error(message)

