import json
import os
from emociones.utils.io import get_base_path

base_path = get_base_path()
preferences_path = os.path.join(base_path, "data", "preferences.json")

with open(preferences_path, "r", encoding="utf-8") as file:
    preferences = json.load(file)