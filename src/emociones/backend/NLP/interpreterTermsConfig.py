development_terms_to_actions = {
    "createAttribute": {
        "terms": ["crear", "atributo", "entidad", "en", "para"],
        "parameters": {
            "attribute": "atributo",  # Palabra clave que precede el valor
            "entity": "entidad"      # Palabra clave que precede el valor
        }
    },
    "createEntity": {
        "terms": ["crear", "entidad"],
        "parameters": {
            "entity": "entidad"
        }
    },
    "deleteAttribute": {
        "terms": ["eliminar", "atributo", "entidad"],
        "parameters": {
            "attribute": "atributo",
            "entity": "entidad"
        }
    },
    "deleteEntity": {
        "terms": ["eliminar", "entidad"],
        "parameters": {
            "entity": "entidad"
        }
    }
}

user_terms_to_actions = {
    "update_collection": {
        "terms": ["actualizar", "coleccion"],
        "parameters": {}
    },
    "face_recognition": {
        "terms": ["identificar", "caras", "rostros"],
        "parameters": {}
    }
}