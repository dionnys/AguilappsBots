import logging
import asyncio
from datetime import datetime
from ClassApi.openai import OpenAI
from aiogram import Bot, Dispatcher, types
from ConnectionDao.mongodb_connection import MongoDBConnection


class TelegramBot:
    def __init__(self, token, openai_api_key):
        self.token = token
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(self.bot)
        logging.basicConfig(level=logging.INFO)


        self.dp.register_message_handler(self.handle_echo)
        self.chatgpt_active_users = {}
        # Crear instancia de la clase OpenAI y configurar la API key
        self.openai_instance = openai_api_key

    async def handle_echo(self, message: types.Message):
        user_id = message.from_user.id
        received_text = message.text.lower()
        user_first_name = message.from_user.first_name
        user_last_name = message.from_user.last_name
        contact = message.contact
        location = message.location
        welcome_message = (f"¡Hola {user_first_name}! en que puedo ayudarte. Escribe /chatgpt para activarlo")

        # Create an instance of the MongoDBConnection class
        self.db_connection = MongoDBConnection()

        # Map commands to functions
        command_functions = {
            '/chatgpt': self.activate_chatgpt,
            '/exit': self.deactivate_chatgpt,
            '/status': self.get_chatgpt_status,
        }

        # Get the function associated with the received command
        command_function = command_functions.get(received_text)

        if command_function:
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
                "contact": contact,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.db_connection.insert_one("conversations", conversation)

        # Send the response to the chat
        await message.answer(response)

    def activate_chatgpt(self, user_id):
        user = {"user_id": user_id,
                "chatgpt_active": True
                }
        # Guardar el estado de activación del chat para el usuario en la base de datos
        self.db_connection.insert_one("users",user)
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
