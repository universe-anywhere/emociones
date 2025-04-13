import spacy

class ChatbotInterpreter:
    def __init__(self, model='es_core_news_sm'):  # Modelo para español
        self.nlp = spacy.load(model)
        
        self.terms_to_actions = {
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

    def interpret(self, text):
        
        # Procesar el texto con spaCy
        doc = self.nlp(text.lower())
        tokenized_text = [token.text for token in doc]  # Lista de palabras extraídas del texto
        print(f"Texto tokenizado: {tokenized_text}")

        # Diccionario para almacenar la mejor acción y parámetros asociados
        best_match = {"action": None, "parameters": {}}
        max_matches = 0
        min_terms = float('inf')  # Inicializar con un valor muy alto para comparar la cantidad de términos

        for action, config in self.terms_to_actions.items():
            terms = config["terms"]
            # Contar los términos que coinciden en el texto
            matches = sum(1 for term in terms if term in tokenized_text)
            print(f"Acción: {action}, Coincidencias: {matches}, Términos definidos: {len(terms)}")
            
            # Actualizar la mejor coincidencia:
            # 1. Si tiene más coincidencias.
            # 2. En caso de empate, se queda con la acción que tiene menos términos definidos.
            if matches > max_matches or (matches == max_matches and len(terms) < min_terms):
                max_matches = matches
                min_terms = len(terms)
                best_match["action"] = action

                # Extraer parámetros basados en la configuración de parámetros
                parameters = {}
                for param_name, keyword in config.get("parameters", {}).items():
                    try:
                        # Buscar el término clave y extraer el siguiente token como valor
                        index = tokenized_text.index(keyword) + 1
                        parameters[param_name] = tokenized_text[index]
                    except (ValueError, IndexError):
                        # Si no se encuentra el término o no hay un valor después, ignorar
                        parameters[param_name] = None
                
                best_match["parameters"] = parameters

        # Devolver la acción con parámetros
        return best_match    