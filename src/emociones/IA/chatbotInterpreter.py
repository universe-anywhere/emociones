import spacy

class ChatbotInterpreter:
    def __init__(self, model='es_core_news_sm'):  # Modelo para español
        self.nlp = spacy.load(model)

    def interpret(self, text):
        doc = self.nlp(text)
        # comentar en version final
        for token in doc:
            print(f"{token.text}: {token.pos_}, {token.dep_}")
        
        text_lower = text.lower()
        # Implementar la lógica personalizada para detectar acciones
        if "crear" in text_lower and "atributo" in text_lower and "entidad" in text_lower:
            # Extraer el atributo y la entidad desde el texto
            words = text.lower().split(" ")
            attribute_index = words.index("atributo") + 1
            entity_index = words.index("entidad") + 1
            attribute_name = words[attribute_index]
            entity_name = words[entity_index]
            return {"action": "create_attribute", "attribute_name": attribute_name, "entity_name": entity_name}
        elif "crear" in text_lower and "entidad" in text_lower:
            return {"action": "create_entity", "name": doc[-1].text}
        return {"action": "unknown"}
    