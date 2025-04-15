import os
import unicodedata
import sounddevice as sd
import vosk
import json
import pyttsx3
import numpy as np  # Asegúrate de importar numpy
from emociones.utils.io import getBasePath
from emociones.preferences import preferences
from emociones.utils.log import logInfo

class ChatBot:
    def __init__(self):
        logInfo("Iniciando el ChatBot")
        # Descargar el modelo de Vosk desde: https://alphacephei.com/vosk/models
        base_path = getBasePath()

        # Construye la ruta completa al modelo desde base_path
        self.model_path = os.path.join(base_path, preferences["chatBoot"]["model_path"])
        logInfo(f"Ruta del modelo: {self.model_path}")
        self.model = vosk.Model(self.model_path)

        # Inicializar el motor de texto a voz
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", preferences["chatBoot"]["rate"])  # Ajusta la velocidad del habla
        self.samplerate = preferences["chatBoot"]["samplerate"]

    def normalizeText(self, text):
        # Eliminar tildes y normalizar el texto
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

    def openChatbotDialog(self):
        transcribed_text = self.listenAndTranscribe()
        logInfo(f"Texto transcrito: {transcribed_text}")
        return transcribed_text

    def speak(self, text):
        """Reproduce el texto dado por los altavoces."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listenAndTranscribe(self, texto=""):
        if (texto != ""):
            self.speak(texto)
        else:  
            self.speak("¿Qué puedo hacer por tí?")  

        # Escucha activa
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype="int16", channels=1) as stream:
            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            logInfo("Escuchando")
            while True:
                data, _ = stream.read(4096)  # Captura el bloque de datos
                # Convierte el flujo de datos a bytes
                data_bytes = np.frombuffer(data, dtype=np.int16).tobytes()
                # Envía los datos al reconocedor
                if rec.AcceptWaveform(data_bytes):
                    result = json.loads(rec.Result())
                    logInfo(f"Transcripción: {result['text']}")
                    return  self.normalizeText(result['text'])