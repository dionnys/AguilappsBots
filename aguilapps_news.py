### See PIN-based authorization for details at
### https://dev.twitter.com/docs/auth/pin-based-authorization

#https://github.com/mattlisiv/newsapi-python
#https://pypi.org/project/cuttpy/


import tweepy
import webbrowser
import os, sys, time
import random
import argparse
import json
from datetime import datetime
import logging as log
from tweepy import OAuthHandler
from newsapi import NewsApiClient
from cuttpy import Cuttpy
import spacy
import pymongo



from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.access_token')

API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_KEY = os.getenv('ACCESS_KEY')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')
API_KEY_NEWS  = os.getenv('API_KEY_NEWS')
API_KEY_CUTT =os.getenv('API_KEY_CUTT')

apinews = NewsApiClient(api_key=API_KEY_NEWS)
# define shortener
cuttly = Cuttpy(API_KEY_CUTT)


#Api credentials
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET,callback="oob")
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

#Modelo neural
nlp = spacy.load("es_core_news_lg")


palabras_violentas = ["asesinato", "violencia", "agresión", "crimen", "muerte", "homicidio", "matar"]

#Conexión de base de datos
client = pymongo.MongoClient(os.getenv('NOSQL_CONNECT'))
db = client["aguilapps"]
collection = db["noticias"]




def authorization():
    # get access token from the user and redirect to auth URL
    auth_url = auth.get_authorization_url()
    print(f'Authorization URL: {auth_url}')
    webbrowser.open(auth_url)
    # ask user to verify the PIN generated in broswer
    verifier = input('PIN: ').strip()
    auth.get_access_token(verifier)

    # Save access token and secret to a file
    with open('.env.access_token', 'w+') as f:
        f.write(f'ACCESS_KEY = "{auth.access_token}"')
        f.write('\n')
        f.write(f'ACCESS_SECRET = "{auth.access_token_secret}"')

    # authenticate and retrieve user name
    auth.set_access_token(auth.access_token, auth.access_token_secret)
    user = api.verify_credentials()
    print(f'Token de cuenta: {user.name} guardado.')




#############################################################################################################################


#Esta función utiliza la API de NewsAPI para buscar
def get_random_articles(question, lang):
    data = apinews.get_everything(q=question, language=lang)
    articles = data["articles"]
    return random.sample(articles, 10)


#Esta función toma una lista de artículos y filtra aquellos que contienen palabras violentas en su título o descripción.
# Devuelve una lista de artículos que no contienen palabras violentas.
def filter_articles(articles):
    filtered_articles = []
    for article in articles:
        titulo_violento = any(palabra in article["title"].lower() for palabra in palabras_violentas)
        descripcion_violenta = any(palabra in article["description"].lower() for palabra in palabras_violentas)
        if not titulo_violento and not descripcion_violenta:
            filtered_articles.append(article)
    return filtered_articles


#sta función toma un artículo y utiliza Spacy para extraer las entidades nombradas (ORG y PERSON) del título y la descripción.
# Luego, utiliza la API de Cuttly para acortar la URL del artículo. La función devuelve un diccionario que contiene el título,
# descripción, URL, entidades nombradas y fecha actual,
# así como una cadena que contiene las entidades nombradas separadas por comas.

def process_article(article):
    doc = nlp(article["title"] + ". " + article["description"])
    entities = [ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.label_ == "PERSON"]
    entities_str = ", ".join(entities)
    shortened_url = cuttly.shorten(article["url"]).shortened_url
    return {
        "title": article["title"],
        "description": article["description"],
        "url": shortened_url,
        "entities": entities,
        "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }, entities_str

#Esta función inserta el diccionario que contiene la información del artículo en la colección de noticias de MongoDB,
#siempre y cuando la URL del artículo no esté ya en la base de datos.

def insert_news(news):
    if collection.count_documents({"url": news["url"]}) == 0:
        collection.insert_one(news)

# Esta función devuelve True si la URL del artículo no está en la colección de noticias de MongoDB y False en caso contrario.
def is_news_new(news):
    return collection.count_documents({"url": news["url"]}) == 0

# Esta función toma un artículo y la cadena que contiene las entidades nombradas,
# y crea un mensaje que se utilizará para publicar el artículo en Twitter.
# El mensaje consta del título del artículo y su URL, y si hay entidades

def create_message(article, entities_str):
    message = f"{article['title']}. {article['url']}"
    if entities_str:
        message = f"{message} - Mencionan: {entities_str}"
    return message

#Esta es la función principal que busca noticias relevantes y publica en Twitter.
# Utiliza las funciones anteriores para buscar artículos aleatorios, filtrarlos, procesarlos y crear un mensaje.

def search_news(question, lang):
    articles = get_random_articles(question, lang)
    filtered_articles = filter_articles(articles)
    for article in filtered_articles:
        news, entities_str = process_article(article)
        if is_news_new(news):
            insert_news(news)
            message = create_message(article, entities_str)
            if len(message) > 280:
                print("La longitud del mensaje supera los 280 caracteres")
            else:
                return message
    return None


#############################################################################################################################

def tweet(message):

        user = api.verify_credentials()
        print(f'Se publicó un tweet en cuenta: {user.name}')
        api.update_status(message)

def get_followers():

    followers = api.get_followers()

    for i in followers:
        print(i)


def get_non_followers():

    followers = api.get_follower_ids()
    friends = api.get_friend_ids()

    non_followers = [user for user in friends if user not in followers]

    # Divide la lista de usuarios que no siguen en bloques de 100
    non_followers_chunks = [non_followers[i:i+100] for i in range(0, len(non_followers), 100)]

    # Busca información completa de usuario para cada bloque de usuarios que no siguen
    non_followers = []
    for chunk in non_followers_chunks:
        user = api.lookup_users(user_id=chunk)
        non_followers.append(user)

    return non_followers



def friends(usuario):
    seguidores = api.get_follower_ids()
    user = api.verify_credentials()
    my_id = user.id
    if my_id in seguidores:
        print("Sí, @" + usuario + " te sigue en Twitter.")
    else:
        print("No, @" + usuario + " no te sigue en Twitter.")



if __name__ == "__main__":
        print('*' * 30, 'INICIO EJECUCION BOTS', '*' * 30)

        try:
                parser = argparse.ArgumentParser()
                parser.add_argument(
                "-a",
                "--authorization",
                action = 'store_true',
                required = False,
                help = "Obtiene los token autorización del usuario.",
                )
                parser.add_argument(
                "-q",
                "--question",
                default = 'python',
                type = str,
                help = "Bots twitter",
                )
                parser.add_argument(
                "-l",
                "--language",
                choices = ['en', 'es'],
                default = 'es',
                type = str,
                required = False,
                help = "Especifica un idioma para la busqueda 'en' (English) o 'es' (Español)",
                )
                parser.add_argument(
                "-g",
                "--getuser",
                action = 'store_true',
                required = False,
                help = "Lista de follower)",
                )
                parser.add_argument(
                "-f",
                "--friends",
                action = 'store_true',
                required = False,
                help = "Especifica un idioma para la busqueda 'en' (English) o 'es' (Español)",
                )

                args = parser.parse_args()
                auth_user = args.authorization
                lang = args.language
                question = args.question
                gfollower = args.getuser
                sfriends = args.friends


                if  auth_user is True :
                        authorization()
                if  gfollower is True :
                        get_followers()
                if  sfriends is True :
                        usuario ='dionnysbonalde'
                        #friends(usuario)
                        non_followers = get_non_followers()
                        for user in non_followers:
                           print(user.screen_name)

                else:
                        result = None
                        noticia = search_news(question, lang)
                        print(noticia)
                        tweet(noticia)



        except Exception as e:
                log.error(f'Error de Ejecucion: {e}')
        finally:
                log.info('FIN - Ejecucion.')
                print('*' * 30, 'FIN - EJECUCION BOTS', '*' * 30)
                sys.exit()
