### See PIN-based authorization for details at
### https://dev.twitter.com/docs/auth/pin-based-authorization

#https://github.com/mattlisiv/newsapi-python
#https://pypi.org/project/cuttpy/


import tweepy
import webbrowser
import os, sys
import datetime
import random
import argparse
import json

import logging as log

from newsapi import NewsApiClient
from cuttpy import Cuttpy
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
cuttly = Cuttpy(API_KEY_CUTT)# define shortener

#Api credentials
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET,callback="oob")
api = tweepy.API(auth)



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

def search_news(question,lang):

        rnum = random.randint(1,9)
        date=datetime.datetime.now().strftime('%Y-%m-%d')
        data=apinews.get_everything(q=question,language=lang)
        articles=data['articles']
        for x in articles[rnum:rnum+1]:
                resp = cuttly.shorten(x['url'])
                message=(f'{x["title"]}. {resp.shortened_url}')
                cant_caracteres = len(message)
                #print('Cantidad de caracteres: ',cant_caracteres,'/280')
        return message

def tweet(message):

        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        user = api.verify_credentials()
        print(f'Se publicó un tweet en cuenta: {user.name}')
        api.update_status(message)







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

                args = parser.parse_args()
                auth_user = args.authorization
                lang = args.language
                question = args.question

                if  auth_user is True :
                        authorization()

                else:
                        noticia = search_news(question, lang)
                        tweet(noticia)
                        #print (noticia)

        except Exception as e:
                log.error(f'Error de Ejecucion: {e}')
        finally:
                log.info('FIN - Ejecucion.')
                print('*' * 30, 'FIN - EJECUCION BOTS', '*' * 30)
                sys.exit()
