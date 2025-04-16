MAX_IMAGE_WIDTH = 150  # Ancho máximo inicial de la imagen
SIDE_MARGIN = 10  # Márgenes izquierdo y derecho iguales
SCROLLBAR_WIDTH = 20 # Ancho típico de la barra de desplazamiento vertical en Qt (aprox. 16-20 px) 
WIDGET_ADDED_WIDTH = 75 # Ancho adicional para pintar un widget

ENTITY_KEY_FOTO = "foto"  # entidad tipo Foto
ENTITY_KEY_VIDEO = "video"  # entidad tipo Video
ENTITY_KEY_CARA = "cara"  # entidad tipo Cara
ENTITY_KEY_MULTIMEDIA = "archivo multimedia"  # entidad tipo Archivo Multimedia

ATTRIBUTE_KEY_JPG = "jpg"  # Atributo JPG indica el formato del archivo contenido en el BLOB
ATTRIBUTE_KEY_RUTA = "ruta"  # Atributo Ruta de la imagen o video
ATTRIBUTE_KEY_FIRMA = "firma"  # Atributo  Firma de la entidad (hash SHA-256) para imagenes (fotos, videos, caras)

RELATIONSHIP_KEY_CAN_BE = "puede ser"  # Relación entre la entidad y el archivo multimedia

IMAGE="image"
VIDEO="video"
GIF_MAX_FRAMES = 10  # Número máximo de frames para un GIF animado
