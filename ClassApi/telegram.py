import os
import re
import time
import random
import string
import logging
import asyncio
import datetime
import validators
from ClassApi.openai import OpenAI
from aiogram import Bot, Dispatcher, types
from Tools.download import Downloader
from ConnectionDao.mongodb_connection import MongoDBConnection


class TelegramBot:
    def __init__(self, token, openai_api_key):
        self.token = token
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(self.bot)
        self.chatgpt_active_users = {}
        self.downloader = Downloader()
        logging.basicConfig(level=logging.INFO)
        self.dp.register_message_handler(self.handle_echo)
        # Crear instancia de la clase OpenAI y configurar la API key
        self.openai_instance = openai_api_key

    async def handle_echo(self, message: types.Message):
        user_id = message.from_user.id
        received_text = message.text.lower()
        user_first_name = message.from_user.first_name
        user_last_name = message.from_user.last_name
        welcome_message = (f"¡Hola {user_first_name}! en que puedo ayudarte. Escribe /chatgpt para activarlo")

        # Create an instance of the MongoDBConnection class
        self.db_connection = MongoDBConnection()

        if "instagram.com" in received_text:
            await self.download_video(user_id, message)
            return

        # Map commands to functions
        command_functions = {
            '/chatgpt': self.activate_chatgpt,
            '/status': self.get_chatgpt_status,
            '/exit': self.deactivate_chatgpt,
            '/downloader': self.download_video,

        }

        # Get the function associated with the received command
        command_function = command_functions.get(received_text)

        if command_function:
            if asyncio.iscoroutinefunction(command_function):
                task = asyncio.create_task(command_function(user_id, message))
                response = await task
            else:
                response = command_function(user_id)

        elif user_id in self.chatgpt_active_users:
            response = self.openai_instance.get_response(received_text)
        else:
            response = welcome_message

        # Save the conversation in MongoDB
        if user_id in self.chatgpt_active_users is not None:

            conversation = {
                "user_id": user_id,
                "user_name": user_first_name,
                "user_last_name": user_last_name,
                "user_message": received_text,
                "bot_message": response,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.db_connection.insert_one("conversations", conversation)

        # Send the response to the chat
        await message.answer(response)

    def activate_chatgpt(self, user_id):
        # Verificar si el chat ya está activo para el usuario
        user = self.db_connection.find_one_documents("users", {"user_id": user_id})
        if user and user.get("chatgpt_active"):
            return "ChatGPT ya está activado."

        # Si el chat no está activo para el usuario, activarlo y almacenar el estado en la base de datos
        user = {"user_id": user_id, "chatgpt_active": True}
        self.db_connection.insert_one("users", user)
        self.chatgpt_active_users[user_id] = True
        return "ChatGPT activado. Escribe tus preguntas y te responderé. Escribe /estatus para saber el estado y /exit para salir."


    def deactivate_chatgpt(self, user_id):
        # Eliminar el estado de activación del chat para el usuario de la base de datos
        self.db_connection.delete_one("users", {"user_id": user_id})
        self.chatgpt_active_users.pop(user_id, None)
        return "ChatGPT desactivado."

    def get_chatgpt_status(self, user_id):
        # Verificar el estado de activación del chat para el usuario en la base de datos
        user = self.db_connection.find_one_documents("users", {"user_id": user_id})
        if user and user.get("chatgpt_active"):
            return "ChatGPT está activado."
        else:
            return "ChatGPT está desactivado."

    async def download_video(self, user_id, message=None):
        post_url = message.text
        target_folder = "downloads"

        # Check if the message contains a valid post URL
        if not validators.url(post_url):
            await message.answer("Por favor, ingresa una URL de publicación válida.")
            return

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        try:
            # Generate a random filename for the video
            shortcode = self.downloader.extract_shortcode(post_url)
            video_file = os.path.join(target_folder, f"{shortcode}.mp4")

            # Check if the URL is from Instagram or YouTube
            if "instagram.com" in post_url:
                # Download the video from Instagram
                await self.downloader.download_video_ig(post_url, target_folder)
            elif "youtube.com" in post_url or "youtu.be" in post_url:
                # Download the video from YouTube
                await self.downloader.download_video_yb(post_url, target_folder)
            else:
                raise ValueError("Invalid video URL")

            # Check if the downloaded file exists
            if not os.path.exists(video_file):
                raise Exception("Error downloading video")

            # Send the video to the chat
            with open(video_file, "rb") as f:
                await message.reply_video(f)

            # Delete the downloaded file
            os.remove(video_file)

        except Exception as e:
            logging.error(e)
            await message.answer("Error al descargar el video. Por favor, comprueba la URL y vuelve a intentarlo.")





    async def start(self, message: types.Message):
        # Obtener el primer nombre del usuario del objeto de mensaje
        user_first_name = message.from_user.first_name

        # Construir el mensaje de bienvenida con el nombre del usuario
        welcome_message = f"¡Hola {user_first_name}! Soy un bot de Telegram. Escribe /chatgpt para activar ChatGPT, /status para saber el estado y /exit para salir."

        # Enviar el mensaje de bienvenida al usuario
        await message.answer(welcome_message)
    async def run(self):
        # Método que inicia el polling del bot
        await self.dp.start_polling()

