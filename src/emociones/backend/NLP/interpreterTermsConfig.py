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
    },
    "show_gallery_preview": {
        "terms": ["mostrar", "resultados", "coleccion"],
        "parameters": {}
    },
    "init_workingCollection": {
        "terms": ["nueva", "busqueda"],
        "parameters": {}
    },
    "filter_workingCollection": {
        "terms": ["seleccionar", "imagenes", "fotos", "videos", "del año"],
        "parameters": {}
    },
    "filter_workingCollection": {
        "terms": ["seleccionar", "imagenes", "fotos", "videos", "del año","al año"],
        "parameters": {}
    },
    "filter_workingCollection": {
        "terms": ["seleccionar", "imagenes", "fotos", "videos", "de los años"],
        "parameters": {}
    }
}