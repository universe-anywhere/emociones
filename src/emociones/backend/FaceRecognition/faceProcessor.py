import cv2
import face_recognition
import numpy as np
import json
import hashlib
import threading
import uuid
from emociones.globals.globalVars import app_context
from emociones.backend.database.databaseHandler import DatabaseHandler
from emociones.backend.database.databaseExceptions import AttributeInstanceNotFoundException, EntityInstanceFromAtributeInstanceNotFoundException    
from emociones.utils.fileUtil import isValidFile, fileType
from emociones.utils.log import logInfo, logWarning, logError
from emociones.constants import VIDEO, IMAGE, ENTITY_KEY_FACE, ENTITY_KEY_MULTIMEDIA, RELATIONSHIP_KEY_APPEARS
from emociones.backend.PeopleRecognition.uniquePersonTracker import UniquePersonTracker

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

    def generateUniqueId(self, data):
        """
        Genera un identificador único basado en el contenido del blob.

        Args:
            data (bytes): Datos binarios (blob) del rostro.

        Returns:
            str: ID único basado en un hash.
        """
        return hashlib.md5(data).hexdigest()

    def detectFaces(self, frame, threshold, filePath, multimediaFileEntityDescription, dbHandlerInstance):
        """
        Detecta rostros en un frame y almacena solo rostros únicos (uso interno).

        Args:
            frame (numpy.ndarray): Imagen o frame de video.
            threshold (float): Umbral de similitud para determinar si es el mismo rostro.
            filePath (str): Ruta del archivo actual donde se detectó el rostro.

        Returns:
            None: Actualiza el diccionario faceData directamente.
        """
        uuidDeteccion = uuid.uuid4()
        logInfo(f"Detectando rostros {uuidDeteccion}")
        faceLocations = face_recognition.face_locations(frame)
        faceEncodings = face_recognition.face_encodings(frame, faceLocations)
        detectedFaces = 0
        for encoding, (top, right, bottom, left) in zip(faceEncodings, faceLocations):
            logInfo(f"Rostro detectado en: {top}, {right}, {bottom}, {left}")
            detectedFaces += 1
            # Comprobar si el rostro ya está almacenado
            matchingIndex = next((index for index, knownFace in enumerate(self.knownFaces)
                                  if np.linalg.norm(encoding - knownFace) < threshold), None)
            try:
                if matchingIndex is None:  # Es un rostro único
                    logInfo("Rostro único detectado.")
                    self.knownFaces.append(encoding)

                    # Extraer rostro y convertirlo a blob
                    face = frame[top:bottom, left:right]
                    _, buffer = cv2.imencode(".jpg", face)
                    blob = buffer.tobytes()

                    # Generar un ID único para el blob
                    uniqueId = self.generateUniqueId(blob)
                    # Agregar al diccionario faceData
                    self.faceData[uniqueId] = {
                        "files": [filePath]
                    }


                    logInfo(f"Rostro único detectado con ID: {uniqueId} y tamaño de blob: {len(blob)} bytes")
                    # Crear el blob y la firma (usamos la conexión de base de datos del hilo)
                    try:
                        dbHandlerInstance.fetchAttributeInstanceUUIDValueBlob(ENTITY_KEY_FACE, uniqueId)    
                        logInfo(f"El rostro con firma {uniqueId} ya existe en el sistema")
                    except AttributeInstanceNotFoundException as e:
                        dbHandlerInstance.insertAttributeInstanceValueBlob(ENTITY_KEY_FACE, blob, uniqueId)
                        logInfo(f"Se ha creado el rostro con firma {uniqueId}")
                        
                else:  # El rostro ya está registrado, actualizar archivos
                    logInfo("El rostro ya se encuentra entre los detectados.")
                    uniqueId = list(self.faceData.keys())[matchingIndex]
                    if filePath not in self.faceData[uniqueId]["files"]:
                        self.faceData[uniqueId]["files"].append(filePath)

                #retrieve the face entity UUID from the database)
                faceEntityUUID = dbHandlerInstance.getAttributeInstanceEntityInstanceUUIDFromUniqueValueText(uniqueId)                
                logInfo(f"UUID del rostro recuperado: {faceEntityUUID}")
                try:
                    #retrieve the multimedia entity UUID from the database
                    multimediaFileInstanceUUID = dbHandlerInstance.getAttributeInstanceEntityInstanceUUIDFromUniqueValueText(filePath)
                except EntityInstanceFromAtributeInstanceNotFoundException as e:
                    logInfo(f"ERROR CAPTURADO -> No existe entidad {ENTITY_KEY_MULTIMEDIA} para {filePath}, añadiendola a la colección de base de datos")
                    multimediaFileInstanceInfo = dbHandlerInstance.aggregateFileToDatabasecollection(multimediaFileEntityDescription,filePath)                    
                    logInfo(f"UUID de {ENTITY_KEY_MULTIMEDIA} recuperado: {multimediaFileInstanceInfo[0]}")
                    multimediaFileInstanceUUID = multimediaFileInstanceInfo[0]

                #insert the relationship between the face and the multimedia entity
                dbHandlerInstance.insertRelationship(RELATIONSHIP_KEY_APPEARS, faceEntityUUID, multimediaFileInstanceUUID)
                logInfo(f"Se ha creado la relación entre el rostro y {ENTITY_KEY_MULTIMEDIA} con UUIDs {faceEntityUUID} y {multimediaFileInstanceUUID}")
                logInfo(f"Rostro procesado")
            except Exception as e:
                logError(f"Error al procesar el rostro: {e}")
                raise
        logInfo(f"Fin deteccion de {ENTITY_KEY_FACE} {uuidDeteccion} - Rostros Detectados: {detectedFaces}")

    def evaluateImageQuality(self, image):
        """
        Evalúa la calidad de la imagen en iluminación y nitidez (uso interno).

        Args:
            image (numpy.ndarray): Imagen a evaluar.

        Returns:
            float: Threshold ajustado según calidad.
        """

        if image is None or image.size == 0:
            logWarning("La imagen está vacía o no se pudo cargar. Se omite la evaluación de calidad.")
            return 0.5  # Devuelve un valor por defecto

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
            self.dbHandler = DatabaseHandler(app_context.chatBoot)  # Acceso al manejador de base de datos
            self.distinctPersonTracker = UniquePersonTracker()
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
                    if not validFile:
                        logWarning(f"Archivo inválido: {filePath}")
                        continue

                    # check if file has been processed before
                    if self.dbHandler.faceDetectionHasBeenDone(filePath):
                        logInfo(f"El archivo {filePath} ya ha sido procesado con anterioridad. Se omite la detección de rostros.")
                        continue
                            
                    try:
                        self.distinctPersonTracker.startNewFile(filePath)
                        self.dbHandler.connection.execute("BEGIN TRANSACTION")  # Iniciar transacción
                        transactionUUID = str(uuid.uuid4())
                        logInfo(f"Iniciada transacción -> {transactionUUID}")
                        file_type = fileType(filePath)
                        if file_type == VIDEO:
                            cap = cv2.VideoCapture(filePath)
                            logInfo(f"Abriendo video: {filePath}")
                            while cap.isOpened():
                                ret, frame = cap.read()
                                if not ret or frame is None:
                                    logWarning(f"Frame vacío o no válido en el video: {filePath}. Finalizando procesamiento del video.")
                                    break  # Sal del bucle si no se puede leer el frame
                                threshold = self.evaluateImageQuality(frame)
                                self.detectFaces(frame, threshold, filePath,ENTITY_KEY_MULTIMEDIA, self.dbHandler)
                                self.distinctPersonTracker.processFrame(frame)
                            cap.release()
                            logInfo(f"Video cerrado: {filePath}")
                        elif file_type == IMAGE:
                            file = r"{}".format(filePath)
                            image = cv2.imread(file)
                            logInfo(f"Abriendo imagen: {file}")
                            if image is None or image.size == 0:
                                logWarning(f"No se ha cargado {file}. Asegúrate de que existe.")
                                continue
                            threshold = self.evaluateImageQuality(image)
                            self.detectFaces(image, threshold, filePath,ENTITY_KEY_MULTIMEDIA,self.dbHandler)
                            self.distinctPersonTracker.processFrame(image)
                            logInfo(f"Imagen cerrada: {file}")
                        else:
                            logWarning(f"Formato no soportado para {filePath}.")
                            continue
                        #Establecer el numero total de personas unicas detectadas en el archivo multimedia actual
                        totalUniquePersonsDetected = self.distinctPersonTracker.getTotalPeopleDetected()
                        self.dbHandler.setTotalNumerDistinctPersonDetectedInFile(filePath,totalUniquePersonsDetected)
                        logInfo(f"Estableciendo marca de detección de rostros ejecutada para {filePath} en la base de datos.")    
                        #Establecer la marca de detección de caras ejecutada para el archivo multimedia actual
                        self.dbHandler.setFaceDetectionHasBeenDone(filePath)
                        self.dbHandler.connection.commit()  # Confirmar la transacción
                        logInfo(f"Finalizada transacción -> {transactionUUID}")

                    except Exception as e:
                        self.dbHandler.connection.rollback()  # Revertir la transacción en caso de error
                        logError(f"Error al procesar {filePath}, rollback done: {e}")
                        logInfo(f"Finalizada transacción -> {transactionUUID}")
                        continue
                    finally:
                        if self.dbHandler.connection.in_transaction:
                            self.dbHandler.connection.rollback()  # Revertir la transacción si está activa
                            logWarning(f"Transacción revertida para {filePath} al estar abierta al final del proceso")
                            logInfo(f"Finalizada transacción -> {transactionUUID}")

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

            if self.processingThread:
                self.processingThread.join()  # Esperar a que el hilo termine

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
