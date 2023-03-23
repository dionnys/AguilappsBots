import os
import re
import time
import random
import string
import logging
import asyncio
import validators
from datetime import datetime
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
        self.user_conversations = {}
        logging.basicConfig(level=logging.INFO)
        self.dp.register_message_handler(self.handle_echo)
        # Crear instancia de la clase OpenAI y configurar la API key
        self.openai_instance = openai_api_key

    async def handle_echo(self, message: types.Message):
        user_id = message.from_user.id
        received_text = message.text.lower()
        user_first_name = message.from_user.first_name
        user_last_name = message.from_user.last_name
        user_username = message.from_user.username
        welcome_message = (f"¡Hola, {user_first_name}! Estoy aquí para ayudarte. 😊 Si deseas activar ChatGPT, simplemente escribe /chatgpt. ¡Espero poder asistirte!")


        # Create an instance of the MongoDBConnection class
        self.db_connection = MongoDBConnection()

        # Check if there is an existing conversation for the user
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []

        # Add user's message to the conversation
        self.user_conversations[user_id].append(f"User: {received_text}")

        # Build the conversation prompt
        conversation_history = "\n".join(self.user_conversations[user_id]) + "\nChatGPT:"


        # Map commands to functions
        command_functions = {
            '/chatgpt': self.activate_chatgpt,
            '/chao': self.deactivate_chatgpt

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
            print('AAAA', user_id)
            # Enviar acción de chat "escribiendo"
            await self.bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            # Obtener respuesta de OpenAI
            response = self.openai_instance.get_response(conversation_history)
        else:
            print('xxxx', user_id)
            #response = self.openai_instance.get_response(conversation_history)
            response = welcome_message



        # Save the conversation in MongoDB
        if user_id in self.chatgpt_active_users is not None:

            conversation = {
                "user_id": user_id,
                "user_username": user_username,
                "user_name": user_first_name,
                "user_last_name": user_last_name,
                "user_message": received_text,
                "bot_message": response,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            }
            self.db_connection.insert_one("conversations", conversation)
        # Add ChatGPT's response to the conversation
        self.user_conversations[user_id].append(f"ChatGPT: {response}")
        # Send the response to the chat
        await message.answer(response)

    def activate_chatgpt(self, user_id):
        # Verificar si el chat ya está activo para el usuario
        user = self.db_connection.find_one_documents("users", {"user_id": user_id})
        if user and user.get("chatgpt_active"):
            status_message = "¡Genial! ChatGPT está listo y activado para ayudarte. No dudes en hacerme cualquier pregunta, estoy aquí para asistirte. 😊"
            return status_message

        # Si el chat no está activo para el usuario, activarlo y almacenar el estado en la base de datos
        user = {"user_id": user_id, "chatgpt_active": True}
        self.db_connection.insert_one("users", user)
        self.chatgpt_active_users[user_id] = True
        # Mensaje de despedida
        activate_message = "¡Hola! Soy ChatGPT, tu amigable asistente. Estoy aquí para ayudarte con tus preguntas. Por favor, adelante, pregúntame cualquier cosa y estaré encantado de responder. Cuando quieras despedirte, simplemente escribe /chao."

        return activate_message

    def deactivate_chatgpt(self, user_id):
        # Eliminar el estado de activación del chat para el usuario de la base de datos
        self.db_connection.delete_one("users", {"user_id": user_id})
        self.chatgpt_active_users.pop(user_id, None)
        farewell_message = "ChatGPT se ha desactivado. Si necesitas ayuda en el futuro, no dudes en activarme nuevamente escribiendo /chatgpt. ¡Hasta la próxima! 😊"
        return farewell_message


    async def start(self, message: types.Message):
        # Obtener el primer nombre del usuario del objeto de mensaje
        user_first_name = message.from_user.first_name

        # Construir el mensaje de bienvenida con el nombre del usuario
        welcome_message = f"¡Hola! {user_first_name} Soy un bot de Telegram equipado con ChatGPT, un asistente inteligente basado en inteligencia artificial. Para activar ChatGPT, escribe /chatgpt. Si deseas salir, simplemente escribe /chao."

        # Enviar el mensaje de bienvenida al usuario
        await message.answer(welcome_message)
    async def run(self):
        # Método que inicia el polling del bot
        await self.dp.start_polling()
