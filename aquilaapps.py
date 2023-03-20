import argparse
import os
import random
import sys
import webbrowser
from datetime import datetime


import spacy
import tweepy
import logging as log
from cuttpy import Cuttpy
from dotenv import load_dotenv
from newsapi import NewsApiClient
from Conexion.mongodb_connection import MongoDBConnection

# Carga las variables de entorno
load_dotenv()
load_dotenv('.env.access_token')

# Variables de configuración
api_key = os.getenv('api_key')
api_key_secret = os.getenv('api_key_secret')
access_key = os.getenv('access_key')
access_secret = os.getenv('access_secret')
api_key_news = os.getenv('api_key_news')
api_key_cutt = os.getenv('api_key_cutt')

# Instancia de los clientes de las APIs
apinews = NewsApiClient(api_key=api_key_news)
cuttly = Cuttpy(api_key_cutt)

# Configuración de la autenticación de Tweepy
auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, callback="oob")
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Carga del modelo de lenguaje Spacy
nlp = spacy.load("es_core_news_lg")

# Lista de palabras violentas
palabras_violentas = ["asesinato", "violencia", "agresión", "crimen", "muerte", "homicidio", "matar"]



# Funciones de autorización
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


###### Funciones para obtener y procesar noticias
def get_random_articles(search_term, lang):
    data = apinews.get_everything(q=search_term, language=lang)
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



# Esta función toma un artículo y la cadena que contiene las entidades nombradas,
# y crea un mensaje que se utilizará para publicar el artículo en Twitter.
# El mensaje consta del título del artículo y su URL, y si hay entidades

def create_message(article, entities_str):
    message = f"{article['title']}. {article['url']}"
    if entities_str:
        message = f"{message} #{entities_str}"
    return message


###### Funciones de Twitter
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

def compare_followers():
    followers = set(api.get_follower_ids())
    following = set(api.get_friend_ids())
    nofriends= list(followers - following)
    return nofriends

def get_user_data(user_ids):
    users = []
    records_inserted = 0
    for i in range(0, len(user_ids), 100):
        chunk = user_ids[i:i+100]
        user_data = api.lookup_users(user_id=chunk)
        users.extend(user_data)

    for user in users:
        user_data={
                "iduser":user.id,
                "urlperfil": f'https://twitter.com/{user.screen_name}' ,
                "username": user.screen_name,
                "imagenperfil":user.profile_image_url,
                "nombre": user.name,
                "localizacion": user.location,
                "descripcion": user.description,
                "cuentacreada":user.created_at,
                "seguidores": user.followers_count,
                "Seguidos": user.friends_count,
                "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        field = 'iduser'
        value = (user.id)
        collection = 'nofollowback'
        user_existe = MongoDBConnection.exists_in_field(collection, field, value)
        if  user_existe == False:
            MongoDBConnection.insert_one(collection, user_data)
            records_inserted += 1

    return records_inserted


def friends(usuario):
    seguidores = api.get_follower_ids()
    user = api.verify_credentials()
    my_id = user.id
    if my_id in seguidores:
        print("Sí, @" + usuario + " te sigue en Twitter.")
    else:
        print("No, @" + usuario + " no te sigue en Twitter.")


#Esta es la función principal que busca noticias relevantes y publica en Twitter.
# Utiliza las funciones anteriores para buscar artículos aleatorios, filtrarlos, procesarlos y crear un mensaje.

def search_news(search_term, lang):
    articles = get_random_articles(search_term, lang)
    filtered_articles = filter_articles(articles)

    for article in filtered_articles:
        news, entities_str = process_article(article)
        field = 'title'
        value = (f'{news["title"]}')
        collection = 'noticias'
        articulo_existe = MongoDBConnection.exists_in_field(collection, field, value)
        if  articulo_existe == False:
            MongoDBConnection.insert_one(collection, news)
            message = create_message(news, entities_str)
            if len(message) > 280:
                print("La longitud del mensaje supera los 280 caracteres")
            else:
                return message
    return None


####################
# Función principal


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
                "-s",
                "--search_term",
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
                parser.add_argument(
                "-c",
                "--comparefriends",
                action = 'store_true',
                required = False,
                help = "compara usuarios seguidores vs sequidos",
                )


                args = parser.parse_args()
                auth_user = args.authorization
                lang = args.language
                search_term = args.search_term
                gfollower = args.getuser
                sfriends = args.friends
                cfriends = args.comparefriends


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
                if  cfriends is True :
                       nofollowback = compare_followers()
                       user_data = get_user_data(nofollowback)

                       print(f"Número de registros insertados:: {user_data}")

                else:
                        noticia = search_news(search_term, lang)
                        print(noticia)
                        tweet(noticia)



        except Exception as e:
                log.error(f'Error de Ejecucion: {e}')
        finally:
                log.info('FIN - Ejecucion.')
                print('*' * 30, 'FIN - EJECUCION BOTS', '*' * 30)
                sys.exit()
