import cv2
import face_recognition
import numpy as np
import json
import hashlib
import threading
from emociones.globals.globalVars import app_context
from emociones.backend.database.databaseHandler import DatabaseHandler
from emociones.utils.fileUtil import isValidFile
from emociones.utils.log import logInfo, logWarning
from emociones.constants import VIDEO, IMAGE, ENTITY_KEY_CARA


class FaceProcessor:
    def __init__(self):
        """
        Inicializa la clase FaceProcessor.
        """
        logInfo("Iniciando FaceProcessor")
        self.knownFaces = []  # Lista para almacenar los embeddings de rostros únicos detectados
        self.faceData = {}  # Diccionario para almacenar IDs únicos y la relación de archivos
        self.processingThread = None  # Hilo para detección de rostros
        self.isRunning = False  # Bandera para evitar múltiples ejecuciones simultáneas
        self.stop_event = threading.Event()  # Evento para detener el hilo
        logInfo("FaceProcessor inicializado")

    def __generateUniqueId(self, data):
        """
        Genera un identificador único basado en el contenido del blob.

        Args:
            data (bytes): Datos binarios (blob) del rostro.

        Returns:
            str: ID único basado en un hash.
        """
        return hashlib.md5(data).hexdigest()

    def __detectFaces(self, frame, threshold, filePath):
        """
        Detecta rostros en un frame y almacena solo rostros únicos (uso interno).

        Args:
            frame (numpy.ndarray): Imagen o frame de video.
            threshold (float): Umbral de similitud para determinar si es el mismo rostro.
            filePath (str): Ruta del archivo actual donde se detectó el rostro.

        Returns:
            None: Actualiza el diccionario faceData directamente.
        """
        logInfo("Detectando rostros")
        faceLocations = face_recognition.face_locations(frame)
        faceEncodings = face_recognition.face_encodings(frame, faceLocations)
        dbHandler = DatabaseHandler(app_context.chatBoot)  # Acceso al manejador de base de datos

        for encoding, (top, right, bottom, left) in zip(faceEncodings, faceLocations):
            logInfo(f"Rostro detectado en: {top}, {right}, {bottom}, {left}")

            # Comprobar si el rostro ya está almacenado
            matchingIndex = next((index for index, knownFace in enumerate(self.knownFaces)
                                  if np.linalg.norm(encoding - knownFace) < threshold), None)

            if matchingIndex is None:  # Es un rostro único
                logInfo("Rostro único detectado.")
                self.knownFaces.append(encoding)

                # Extraer rostro y convertirlo a blob
                face = frame[top:bottom, left:right]
                _, buffer = cv2.imencode(".jpg", face)
                blob = buffer.tobytes()

                # Generar un ID único para el blob
                uniqueId = self.__generateUniqueId(blob)

                # Agregar al diccionario faceData
                self.faceData[uniqueId] = {
                    "files": [filePath]
                }

                logInfo(f"Rostro único detectado con ID: {uniqueId} y tamaño de blob: {len(blob)} bytes")
                # Crear el blob y la firma (usamos la conexión de base de datos del hilo)
                result = dbHandler.insertAttributeInstanceValueBlob(ENTITY_KEY_CARA, blob, uniqueId)
                if result is None:
                    logInfo(f"El rostro con firma {uniqueId} ya existe en el sistema")
                else: 
                    logInfo(f"Se ha creado el rostro con firma {uniqueId}")
            else:  # El rostro ya está registrado, actualizar archivos
                logInfo("El rostro ya se encuentra entre los detectados.")
                uniqueId = list(self.faceData.keys())[matchingIndex]
                if filePath not in self.faceData[uniqueId]["files"]:
                    self.faceData[uniqueId]["files"].append(filePath)

    def __evaluateImageQuality(self, image):
        """
        Evalúa la calidad de la imagen en iluminación y nitidez (uso interno).

        Args:
            image (numpy.ndarray): Imagen a evaluar.

        Returns:
            float: Threshold ajustado según calidad.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)

        if brightness > 180 and blur > 150:
            return 0.6
        elif brightness < 100 or blur < 50:
            return 0.7
        else:
            return 0.5

    def processFiles(self, filePaths):
        """
        Procesa imágenes y videos para detectar rostros únicos.

        Args:
            filePaths (list): Lista de rutas de imágenes o videos.

        Returns:
            None: El proceso se ejecuta en un hilo separado si no hay otro proceso en ejecución.
        """
        if self.isRunning:
            app_context.chatBoot.speak("Ya hay un proceso de detección de rostros en ejecución. Por favor, espera a que termine.")
            logWarning("El proceso de detección de rostros ya está en ejecución. Por favor, espera a que termine.")
            return

        def runDetection():
            # Activar las banderas
            self.isRunning = True
            self.stop_event.clear()  # Reinicia el evento al iniciar
            app_context.chatBoot.speak("Iniciando detección de rostros. Puede continuar trabajando con la aplicación.")
            logInfo("Iniciando procesamiento de archivos")

            try:
                for filePath in filePaths:
                    # solo permitimos detener el evento si esta al comienzo de un nuevo fichero (filePath)
                    if self.stop_event.is_set():  # Detener el hilo si el evento está activado
                        logInfo("Solicitud manual de detención del proceso.")
                        return

                    logInfo(f"Procesando: {filePath}")
                    validFile = isValidFile(filePath)
                    if validFile is None:
                        logWarning(f"Archivo inválido: {filePath}")
                        continue

                    if validFile[1] == VIDEO:
                        cap = cv2.VideoCapture(filePath)
                        logInfo(f"Abriendo video: {filePath}")
                        while cap.isOpened():
                            ret, frame = cap.read()
                            threshold = self.__evaluateImageQuality(frame)
                            self.__detectFaces(frame, threshold, filePath)
                        cap.release()
                        logInfo(f"Video cerrado: {filePath}")
                    elif validFile[1] == IMAGE:
                        file = r"{}".format(filePath)
                        image = cv2.imread(file)
                        logInfo(f"Abriendo imagen: {file}")
                        if image is None:
                            logWarning(f"No se ha cargado {file}. Asegúrate de que existe.")
                            continue
                        threshold = self.__evaluateImageQuality(image)
                        self.__detectFaces(image, threshold, filePath)
                        logInfo(f"Imagen cerrada: {file}")
                    else:
                        logWarning(f"Formato no soportado para {filePath}.")
                        continue

                app_context.chatBoot.speak("Finalizada la detección de rostros.")
                logInfo("Terminado procesamiento de archivos")

                json_data = json.dumps(self.faceData, indent=4)
                logInfo(f"Datos de rostros detectados:\n{json_data}")
                app_context.chatBoot.speak("Se ha generado el reporte del proceso.")
            finally:
                self.isRunning = False
                logInfo("El proceso de detección de rostros ha finalizado.")

        # Iniciar el proceso en un hilo separado
        self.processingThread = threading.Thread(target=runDetection)
        self.processingThread.start()
        logInfo("Proceso de detección de rostros lanzado en un hilo separado.")

    def stopDetection(self):
        """
        Detiene el proceso de detección de rostros.
        """
        if self.isRunning:
            logInfo("Solicitando detención del hilo de detección...")
            self.stop_event.set()  # Activar el evento para detener el hilo
            self.isRunning = False
            logInfo("Proceso de detección detenido completamente.")
        else:
            logInfo("No hay procesos en ejecución para detener.")

    def waitForCompletion(self):
        """
        Espera a que el hilo de detección termine.
        """
        if self.processingThread:
            self.processingThread.join()
