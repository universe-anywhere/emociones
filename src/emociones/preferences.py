import json
import os
from emociones.utils.io import getBasePath

preferences_path = os.path.join(getBasePath(), "data", "preferences.json")

with open(preferences_path, "r", encoding="utf-8") as file:
    preferences = json.load(file)