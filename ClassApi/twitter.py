import os
import tweepy
import webbrowser
from datetime import datetime
from dotenv import load_dotenv
from ClassLogManager.log_manager import LogManager
from ConnectionDao.mongodb_connection import MongoDBConnection



# Carga las variables de entorno
load_dotenv()


# Variables de configuración
api_key = os.getenv('api_key')
api_key_secret = os.getenv('api_key_secret')


class Twitter:
    def __init__(self, id_setting, access_key, access_secret):
            self.auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, callback="oob")
            self.auth.set_access_token(access_key, access_secret)
            self.api = tweepy.API(self.auth)
            self.id_setting = id_setting

    def get_authorization(self):
        # get access token from the user and redirect to auth URL

        auth_url = self.auth.get_authorization_url()
        LogManager.log("INFO", f'Authorization URL: {auth_url}')
        print(f'Authorization URL: {auth_url}')
        webbrowser.open(auth_url)
        # ask user to verify the PIN generated in broswer
        verifier = input('PIN: ').strip()
        self.auth.get_access_token(verifier)
        filter = {"_id": self.id_setting}
        update_token = {"$set": {"token_user_twitter": {"access_key": self.auth.access_token, "access_secret": self.auth.access_token_secret}}}
        MongoDBConnection.update_one('setting', filter, update_token )

        # authenticate and retrieve user name
        self.auth.set_access_token(self.auth.access_token, self.auth.access_token_secret)
        user = self.api.verify_credentials()
        user_obj = (user._json)
        MongoDBConnection.insert_one('userinfo', user_obj)
        LogManager.log("INFO", f'Token de cuenta: {user.name} guardado.')



    def set_tweet(self, message):
        user = self.api.verify_credentials()
        LogManager.log("INFO", f'Se publicó un tweet en cuenta: {user.name}')

        print(f'Se publicó un tweet en cuenta: {user.name}')
        self.api.update_status(message)

    def get_followers(self):
        followers = self.api.get_follower_ids()
        return followers

    def get_following(self):
        following = self.api.get_friend_ids()
        return following

    def nofollowback(self):
        followers = set(self.api.get_follower_ids())
        following = set(self.api.get_friend_ids())
        nofriends = list(followers - following)
        return nofriends

    def followback(self):
        followers = set(self.api.get_follower_ids())
        following = set(self.api.get_friend_ids())
        friends = followers.intersection(following)
        return list(friends)

    def get_blockedaccounts(self):
        blockeds = (self.api.get_blocked_ids())
        return blockeds

    def get_mutedsaccounts(self):
        blockeds = (self.api.get_muted_ids())
        return blockeds

    def get_user_data(self, collection, user_ids):
        users = []
        records_inserted = 0
        for i in range(0, len(user_ids), 100):
            chunk = user_ids[i:i+100]
            user_data = self.api.lookup_users(user_id=chunk)
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


            query_user_existe = {"iduser": user.id}
            user_existe = MongoDBConnection.find_one_documents(collection, query_user_existe)

            if not user_existe:
                MongoDBConnection.insert_one(collection, user_data)
                records_inserted += 1
            else:
                user_compare = user_data.copy()
                user_history = user_existe.copy()
                del user_compare["date"]
                del user_compare["urlperfil"]
                del user_compare["cuentacreada"]
                del user_history["_id"]
                del user_history["urlperfil"]
                del user_history["date"]
                del user_history["cuentacreada"]
                insert_history = user_existe.copy()
                del insert_history["_id"]
                insert_history["sourcecollection"] = collection

                if user_compare != user_history:
                    collection_history = "history"
                    query_user_data = {"iduser": user.id}
                    update_user_data = {"$set": user_data}
                    MongoDBConnection.insert_one(collection_history, insert_history)
                    MongoDBConnection.update_one(collection, query_user_data, update_user_data)
                else:
                    pass

        return records_inserted
