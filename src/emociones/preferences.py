import json
import sys
import os

# Cargar las preferencias desde preferences.json
if getattr(sys, "frozen", False):  # Si está empaquetado con PyInstaller
    base_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller coloca los archivos
else:  # Modo desarrollo
    base_path = os.path.dirname(__file__)  # Carpeta donde está preferences.py

# Ruta completa al archivo preferences.json
preferences_path = os.path.join(base_path, "data", "preferences.json")

with open(preferences_path, "r", encoding="utf-8") as file:
    preferences = json.load(file)