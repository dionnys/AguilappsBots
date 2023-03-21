
import os
import sys
import argparse
from datetime import datetime
from ConnectionDao.mongodb_connection import MongoDBConnection
from ClassApi.news import News
from ClassApi.twitter import Twitter
from ClassLogManager.log_manager import LogManager


#configuracion
setting = MongoDBConnection.find_documents('setting')

for configs in setting:
    id_setting = configs['_id']
    banned_words = configs['bannedwords']
    access_key = (configs['token_user']['access_key'])
    access_secret = (configs['token_user']['access_secret'])
    api_key_news = (configs['apikeynews'])
    api_key_cutt = (configs['apikeycutt'])

# Creación del objeto News
news = News(api_key_news, api_key_cutt, banned_words)

# Creación del objeto Twitter
twitter = Twitter(id_setting, access_key, access_secret)



####################
# Función principal
def main():
    action_mapping = {
        'authorization': twitter.get_authorization,
        'postnew': lambda: twitter.set_tweet(news.search_news(postnews, lang)),
        'followers': lambda: twitter.get_user_data('followers', twitter.get_followers()),
        'following': lambda: twitter.get_user_data('following', twitter.get_following()),
        'nofollowback': lambda: twitter.get_user_data('nofollowback', twitter.nofollowback()),
        'followback': lambda: twitter.get_user_data('followback', twitter.followback()),
        'blocked': lambda: twitter.get_user_data('blockedaccounts', twitter.get_blockedaccounts()),
        'muted': lambda: twitter.get_user_data('mutedaccounts', twitter.get_mutedsaccounts()),
    }

    executed = False
    for arg, func in action_mapping.items():
        if getattr(args, arg):
            result = func()
            print(f"Resultado de {arg}: {result}")
            executed = True

    if not executed:
        print(f'Seleccione una opción: -h para ayuda')


if __name__ == "__main__":
        print('*' * 30, 'INICIO EJECUCION BOTS', '*' * 30)
        LogManager.log("INFO", "INICIO EJECUCION BOTS")

        try:
                parser = argparse.ArgumentParser()
                parser.add_argument(
                "-a",
                "--authorization",
                action = 'store_true',
                required = False,
                help = "Obtiene los token autorización del usuario."
                )
                parser.add_argument(
                "-news",
                "--postnew",
                type = str,
                help = "Publica noticias en twiter."
                )
                parser.add_argument(
                "-l",
                "--language",
                choices = ['en', 'es'],
                default = 'es',
                type = str,
                required = False,
                help = "Especifica un idioma para la busqueda 'en' (English) o 'es' (Español)"
                )
                parser.add_argument(
                "-fs",
                "--followers",
                action = 'store_true',
                required = False,
                help = "Lista de seguidores."
                )
                parser.add_argument(
                "-fw",
                "--following",
                action = 'store_true',
                required = False,
                help = "Lista de seguidos."
                )
                parser.add_argument(
                "-ff",
                "--followback",
                action = 'store_true',
                required = False,
                help = "Lista de seguidos de vuelta (Followback)."
                )
                parser.add_argument(
                "-fb",
                "--nofollowback",
                action = 'store_true',
                required = False,
                help = "Lista de no seguidos de vuelta (Notfollowback)."
                )
                parser.add_argument(
                "-bck",
                "--blocked",
                action = 'store_true',
                required = False,
                help = "Lista de cuentas bloqueadas."
                )
                parser.add_argument(
                "-m",
                "--muted",
                action = 'store_true',
                required = False,
                help = "Lista de cuentas silenciadas."
                )


                args = parser.parse_args()
                auth_user = args.authorization
                lang = args.language
                postnews = args.postnew
                followers = args.followers
                following = args.following
                notfollowback = args.nofollowback
                followbacks = args.followback
                blockeds = args.blocked
                muteds = args.muted

                main()

        except Exception as e:
            LogManager.log("ERROR", f'Error de Ejecucion: {e}')
        finally:
            LogManager.log("INFO", f'FIN - EJECUCION BOTS')
            print('*' * 30, 'FIN - EJECUCION BOTS', '*' * 30)
            sys.exit()