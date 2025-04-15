import spacy
from emociones.utils.log import log_info

class ChatbotInterpreter:
    def __init__(self, model='es_core_news_sm'):  # Modelo para español
        self.nlp = spacy.load(model)
        

    def interpret(self, text, action_terms):
        
        # Procesar el texto con spaCy
        doc = self.nlp(text.lower())
        tokenized_text = [token.text for token in doc]  # Lista de palabras extraídas del texto
        log_info(f"Texto tokenizado: {tokenized_text}")  # Para depuración

        # Diccionario para almacenar la mejor acción y parámetros asociados
        best_match = {"action": None, "parameters": {}}
        max_matches = 0
        min_terms = float('inf')  # Inicializar con un valor muy alto para comparar la cantidad de términos

        for action, config in action_terms.items():
            terms = config["terms"]
            # Contar los términos que coinciden en el texto
            matches = sum(1 for term in terms if term in tokenized_text)
            log_info(f"Acción: {action}, Coincidencias: {matches}, Términos definidos: {len(terms)}")  # Para depuración
            
            # Actualizar la mejor coincidencia:
            # 1. Si tiene más coincidencias.
            # 2. En caso de empate, se queda con la acción que tiene menos términos definidos.
            if matches > max_matches or (matches > 0 and matches == max_matches and len(terms) < min_terms):
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