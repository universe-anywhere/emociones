MAX_IMAGE_WIDTH = 150  # Ancho máximo inicial de la imagen
SIDE_MARGIN = 10  # Márgenes izquierdo y derecho iguales
SCROLLBAR_WIDTH = 20 # Ancho típico de la barra de desplazamiento vertical en Qt (aprox. 16-20 px) 
WIDGET_ADDED_WIDTH = 75 # Ancho adicional para pintar un widget

ENTITY_KEY_FACE = "cara"  # entidad tipo Cara
ENTITY_KEY_MULTIMEDIA = "archivo multimedia"  # entidad tipo Archivo Multimedia

ATTRIBUTE_KEY_JPG = "jpg"  # Atributo JPG indica el formato del archivo contenido en el BLOB
ATTRIBUTE_KEY_PATH = "ruta"  # Atributo Ruta de la imagen o video
ATTRIBUTE_KEY_SIGNATURE = "firma"  # Atributo  Firma de la entidad (hash SHA-256) para imagenes (fotos, videos, caras)
ATTRIBUTE_KEY_FACEDECTION_DONE = "dectección de cara ejecutada"  # Atributo que indica si se ha realizado la detección de cara en la imagen o video
ATTRIBUTE_KEY_DICTINCT_PERSON_COUNT = "número de personas únicas detectadas"

RELATIONSHIP_KEY_APPEARS = "aparece en"  # Relación entre cara y foto/video

IMAGE="image"
VIDEO="video"
GIF_MAX_FRAMES = 10  # Número máximo de frames para un GIF animado
