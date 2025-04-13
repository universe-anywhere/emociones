import sounddevice as sd
import vosk
import json
import pyttsx3
import numpy as np  # Asegúrate de importar numpy
from emociones.preferences import preferences

class ChatBot:
    def __init__(self):
        print("Iniciando el ChatBot...")
        # Descargar el modelo de Vosk desde: https://alphacephei.com/vosk/models
        self.model_path = preferences["chatBoot"]["model_path"]  # Ruta donde se almacena el modelo
        self.model = vosk.Model(self.model_path)

        # Inicializar el motor de texto a voz
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", preferences["chatBoot"]["rate"])  # Ajusta la velocidad del habla
        self.samplerate = preferences["chatBoot"]["samplerate"]

    def open_chatbot_dialog(self):
        print("Chat bot...")
        transcribed_text = self.listen_and_transcribe()
        print(f"Texto transcrito: {transcribed_text}")

    def speak(self, text):
        """Reproduce el texto dado por los altavoces."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_and_transcribe(self):
        """Escucha al usuario y transcribe sin límite de tiempo."""
        self.speak("Espere 3 segundos y diga algo...")  # Reproducir "Diga algo" por los altavoces

        # Escucha activa
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype="int16", channels=1) as stream:
            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            print("Escuchando...")
            while True:
                data, _ = stream.read(4096)  # Captura el bloque de datos
                # Convierte el flujo de datos a bytes
                data_bytes = np.frombuffer(data, dtype=np.int16).tobytes()
                # Envía los datos al reconocedor
                if rec.AcceptWaveform(data_bytes):
                    result = json.loads(rec.Result())
                    print(f"Transcripción: {result['text']}")
                    return result['text']