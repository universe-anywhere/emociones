import os
import torch
import numpy as np
import cv2
import traceback
from emociones.utils.log import logInfo, logWarning
from emociones.utils.io import getBasePath
from emociones.preferences import preferences
from emociones.yolov5.models.common import DetectMultiBackend
from emociones.yolov5.utils.general import check_img_size


class UniquePersonTracker:
    def __init__(self):
        modelPath = os.path.join(getBasePath(), preferences["yolov5"]["model"])        
        logInfo('Inicializando detector de personas únicas con YOLOv5')
        device = "cuda" if torch.cuda.is_available() else "cpu"
        #self.model = torch.hub.load("ultralytics/yolov5", "yolov5s")  # Can be 'yolov5n' - 'yolov5x6', or 'custom'
        self.model = DetectMultiBackend(modelPath, device=device)  # Usa "cuda" si hay GPU disponible        
        self.model.conf = 0.25  # Ajustar confianza mínima de detección
        self.iouThreshold = 0.5
        self.currentFilePath = None
        self.trackedPeople = []
        self.frameCount = 0
        logInfo("Inicializado detector de personas únicas con YOLOv5")

    def startNewFile(self, filePath):
        """
        Inicializa el rastreador para un nuevo archivo (imagen o video).
        """
        logInfo(f"Inicializando variables para detección de personas únicas por incorporación de nuevo archivo {filePath}")
        self.currentFilePath = filePath
        self.trackedPeople = []
        self.frameCount = 0
        logInfo(f"Fin de inicialización de variables para detección de personas únicas en archivo {filePath}")

    def processFrame(self, frame):
        """Procesa un frame para detectar personas."""
        self.frameCount += 1
        logInfo(f"Procesando frame {self.frameCount} de archivo {self.currentFilePath}")

        # Ajustar tamaño de la imagen
        imgsz = check_img_size(640, s=self.model.stride)
        test_image_real = cv2.resize(frame, (imgsz, imgsz))
        test_image_real = cv2.cvtColor(test_image_real, cv2.COLOR_BGR2RGB)

        # Convertir la imagen a tensor
        test_image_tensor = torch.tensor(test_image_real).permute(2, 0, 1).unsqueeze(0).to(self.model.device).float()

        # Realizar la detección de objetos con YOLOv5
        try:
            results = self.model(test_image_tensor)  # Ejecutar inferencia

            # Verificar si los resultados tienen el atributo `xyxy` y si hay detecciones válidas
            if hasattr(results, "xyxy") and len(results.xyxy) > 0:
                detections = results.xyxy[0].cpu().numpy()  # Convertir detecciones a NumPy
            else:
                detections = results[0] if isinstance(results, list) and len(results) > 0 else None

                # Verificar si las detecciones son válidas
                if detections is None or detections.shape[1] < 6:
                    logInfo("No se encontraron detecciones útiles en los resultados.")
                    return

            # Extraer coordenadas (bounding boxes), confianza y clases
            coordenadas_np = detections[:, :4].cpu().numpy()  # Coordenadas [xmin, ymin, xmax, ymax]
            confidencias_np = detections[:, 4].cpu().numpy().flatten()  # Convertir a array 1D para evitar errores
            clases_np = detections[:, 5].cpu().numpy().astype(int).flatten()  # Convertir a array 1D de enteros

            # Filtrar detecciones que sean personas (clase 0) y tengan una confianza mínima
            umbral_confianza = 0.25
            # Ensure `coordenadas_np` has shape (85, 4)
            coordenadas_np = coordenadas_np.squeeze().T  # Remove extra dimensions and transpose

            # Now filter correctly
            boundingBoxes = [coordenadas_np[i] for i in range(len(clases_np)) if clases_np[i] == 0 and confidencias_np[i] >= umbral_confianza]

            # Verificar si se detectaron personas y actualizar el seguimiento si es necesario
            if boundingBoxes:
                self.updateTrackedPeople(boundingBoxes)  # Actualizar el seguimiento de personas
            else:
                logInfo("No se detectaron personas en el proceso del frame {self.frameCount} de archivo {self.currentFilePath}")
        except Exception as e:
            traceback.print_exc()  # Mostrar la traza del error para depuración
            logWarning(f"Error durante la inferencia: {e}")  # Registrar el error

    def updateTrackedPeople(self, boundingBoxes):
        """
        Actualiza la lista de personas rastreadas con nuevas detecciones.
        """
        newUniquePersonsDetectedInFrame = 0
        logInfo(f"Detectando personas distintas en frame {self.frameCount}")

        for box in boundingBoxes:
            newPerson = True

            for tracked in self.trackedPeople:
                iou = self.iou(tracked["bbox"], box)
                if iou > self.iouThreshold:
                    tracked["bbox"] = box
                    tracked["lastSeen"] = self.frameCount
                    newPerson = False
                    break

            if newPerson:
                newUniquePersonsDetectedInFrame += 1
                self.trackedPeople.append({"bbox": box, "firstSeen": self.frameCount, "lastSeen": self.frameCount})
                logInfo(f"Nueva persona detectada {len(self.trackedPeople)}")

        logInfo(f"Fin detección de personas distintas en frame {self.frameCount}, detectadas  {len(boundingBoxes)} de las cuales únicas son {newUniquePersonsDetectedInFrame} personas nuevas en el Frame")

    def getTotalPeopleDetected(self):
        """
        Devuelve el número total de personas únicas detectadas.
        """
        logInfo(f"Solicitado número total de personas únicas detectadas: {len(self.trackedPeople)}")
        return len(self.trackedPeople)

    def iou(self, box1, box2):
        """
        Calcula el índice de intersección sobre unión (IoU) entre dos cuadros delimitadores.
        """
        x1, y1, x2, y2 = box1
        x3, y3, x4, y4 = box2

        xi1, yi1 = max(x1, x3), max(y1, y3)
        xi2, yi2 = min(x2, x4), min(y2, y4)
        intersection = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        box1Area = (x2 - x1) * (y2 - y1)
        box2Area = (x4 - x3) * (y4 - y3)
        union = box1Area + box2Area - intersection

        return intersection / union if union > 0 else 0
    
