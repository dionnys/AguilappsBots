import random
import spacy
from datetime import datetime
from cuttpy import Cuttpy
from newsapi import NewsApiClient
from ClassLogManager.log_manager import LogManager
from ConnectionDao.mongodb_connection import MongoDBConnection

class News:
    def __init__(self, api_key_news, api_key_cutt, banned_words):
        self.apinews = NewsApiClient(api_key=api_key_news)
        self.cuttly = Cuttpy(api_key_cutt)
        self.nlp = spacy.load("es_core_news_lg")
        self.banned_words = banned_words

    def get_random_articles(self, search_term, lang):
        try:
            data = self.apinews.get_everything(q=search_term, language=lang)
            articles = data["articles"]
            return random.sample(articles, 10)
        except Exception as e:
            LogManager.log("ERROR", f"Ocurrió un error al obtener artículos: {str(e)}")
            return []

    def filter_articles(self, articles):
        try:
            filtered_articles = []
            for article in articles:
                titulo_violento = any(palabra in article["title"].lower() for palabra in self.banned_words)
                descripcion_violenta = any(palabra in article["description"].lower() for palabra in self.banned_words)
                if not titulo_violento and not descripcion_violenta:
                    filtered_articles.append(article)
            return filtered_articles
        except Exception as e:
            LogManager.log("ERROR", f"Ocurrió un error al filtrar los artículos: {str(e)}")
            return []

    def process_article(self, article):
        try:
            # Verificar que el artículo tenga las claves esperadas
            if "title" in article and "description" in article and "url" in article:
                doc = self.nlp(article["title"] + ". " + article["description"])
                entities = [ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.label_ == "PERSON"]
                entities_str = ", ".join(entities)
                shortened_url = self.cuttly.shorten(article["url"]).shortened_url
                return {
                    "title": article["title"],
                    "description": article["description"],
                    "url": shortened_url,
                    "entities": entities,
                    "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }, entities_str
            else:
                raise ValueError("El artículo no tiene las claves esperadas.")
        except Exception as e:
            LogManager.log("ERROR", f"Ocurrió un error al procesar el artículo: {str(e)}")
            return None, ""

    def create_message(self, article, entities_str):
        try:
            # Verificar que el artículo tenga las claves esperadas
            if "title" in article and "url" in article:
                message = f"{article['title']}. {article['url']}"
                if entities_str:
                    message = f"{message} #{entities_str}"
                return message
            else:
                raise ValueError("El artículo no tiene las claves esperadas.")
        except Exception as e:
            LogManager.log("ERROR", f"Ocurrió un error al crear el mensaje: {str(e)}")
            return ""

    def search_news(self, search_term, lang):
        try:
            articles = self.get_random_articles(search_term, lang)
            filtered_articles = self.filter_articles(articles)
            for article in filtered_articles:
                news, entities_str = self.process_article(article)
                collection = 'news'
                query_articulo_existe = {"title": news["title"]}
                articulo_existe = MongoDBConnection.exists_in_field(collection, query_articulo_existe)
                if articulo_existe == False:
                    MongoDBConnection.insert_one(collection, news)
                    message = self.create_message(news, entities_str)
                    if len(message) > 280:
                        LogManager.log("INFO", f"La longitud del mensaje supera los 280 caracteres")
                    else:
                        return message
            return None
        except Exception as e:
            LogManager.log("ERROR", f"Ocurrió un error al buscar noticias: {str(e)}")
            return None