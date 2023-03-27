import spacy
from spacy.util import minibatch, compounding


class SpacyProcessor:
    def __init__(self, spacy_model_name):
        spacy.prefer_gpu()
        self.nlp = spacy.load(spacy_model_name)


    def analyze_message(self, message):
        """
        Analiza un mensaje usando spaCy y devuelve un diccionario con las
        siguientes claves:
            - entities: lista de entidades detectadas en el mensaje
            - nouns: lista de sustantivos detectados en el mensaje
            - adjectives: lista de adjetivos detectados en el mensaje
            - verbs: lista de verbos detectados en el mensaje
            - adverbs: lista de adverbios detectados en el mensaje
            - pronouns: lista de pronombres detectados en el mensaje
            - prepositions: lista de preposiciones detectadas en el mensaje
            - conjunctions: lista de conjunciones detectadas en el mensaje
        """
        doc = self.nlp(message)
        entities = [ent.text for ent in doc.ents]
        nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
        verbs = [token.text for token in doc if token.pos_ == "VERB"]
        adverbs = [token.text for token in doc if token.pos_ == "ADV"]
        pronouns = [token.text for token in doc if token.pos_ == "PRON"]
        prepositions = [token.text for token in doc if token.pos_ == "ADP"]
        conjunctions = [token.text for token in doc if token.pos_ == "CCONJ" or token.pos_ == "SCONJ"]
        return {
            "entities": entities,
            "nouns": nouns,
            "adjectives": adjectives,
            "verbs": verbs,
            "adverbs": adverbs,
            "pronouns": pronouns,
            "prepositions": prepositions,
            "conjunctions": conjunctions
        }

    def dependency_parsing(self, message):
        doc = self.nlp(message)
        dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
        return dependencies

    def semantic_similarity(self, message1, message2):
        doc1 = self.nlp(message1)
        doc2 = self.nlp(message2)
        similarity = doc1.similarity(doc2)
        return similarity

    def custom_tokenization(self, message):
        def custom_tokenizer(nlp):
            # Crear una función personalizada para la tokenización aquí
            pass
        self.nlp.tokenizer = custom_tokenizer(self.nlp)
        doc = self.nlp(message)
        tokens = [token.text for token in doc]
        return tokens

    def extract_key_phrases(self, message):
        doc = self.nlp(message)
        key_phrases = [chunk.text for chunk in doc.noun_chunks]
        return key_phrases
