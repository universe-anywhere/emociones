development_terms_to_actions = {
    "create_attribute": {
        "terms": ["crear", "atributo", "entidad", "en", "para"],
        "parameters": {
            "attribute": "atributo",  # Palabra clave que precede el valor
            "entity": "entidad"      # Palabra clave que precede el valor
        }
    },
    "create_entity": {
        "terms": ["crear", "entidad"],
        "parameters": {
            "entity": "entidad"
        }
    },
    "delete_attribute": {
        "terms": ["eliminar", "atributo", "entidad"],
        "parameters": {
            "attribute": "atributo",
            "entity": "entidad"
        }
    },
    "delete_entity": {
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
    }
}