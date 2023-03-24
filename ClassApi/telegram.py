import os
import re
import time
import random
import string
import logging
import asyncio
import validators
import spacy
from spacy.util import minibatch, compounding
from datetime import datetime
from ClassApi.openai import OpenAI
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from Tools.managers_tasks import TaskHandler
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from ConnectionDao.mongodb_connection import MongoDBConnection




class TelegramBot:
    def __init__(self, token, openai_api_key, spacy_model_default):
        self.token = token
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(self.bot)
        self.dp.middleware.setup(LoggingMiddleware())
        self.chatgpt_active_users = {}
        self.user_conversations = {}
        self.spacy_model_name_default = spacy_model_default
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
        welcome_message = (f"¡Hola, {user_first_name}! Estoy aquí para ayudarte. 😊 Si deseas activar ChatGPT, simplemente escribe /hola. ¡Espero poder asistirte!")


        # Create an instance of the MongoDBConnection class
        self.db_connection = MongoDBConnection()

        # Check if there is an existing conversation for the user
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []

        # Add user's message to the conversation
        self.user_conversations[user_id].append(f"User: {received_text}")

        # Build the conversation prompt
        conversation_history = "\n".join(self.user_conversations[user_id]) + "\nChatGPT:"


        # Verificar si el usuario ya tiene datos almacenados en la base de datos
        user_data = self.db_connection.find_one_documents("users", {"user_id": user_id})
        if user_data:
            # Si ya existe un documento para el usuario, actualizar los datos del usuario
            user_data_update = {
                "user_name": user_first_name,
                "user_last_name": user_last_name,
                "user_username": user_username,
                "last_interaction_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.db_connection.update_one("users", {"user_id": user_id}, {"$set": user_data_update})
        else:
            # Si no existe un documento para el usuario, insertar uno nuevo
            user_data = {
                "user_id": user_id,
                "chatgpt_active": False,
                "spacy_model": self.spacy_model_name_default,
                "banned_gpt": False,
                "banned_chat": False,
                "user_name": user_first_name,
                "user_last_name": user_last_name,
                "user_username": user_username,
                "activation_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "last_interaction_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.db_connection.insert_one("users", user_data)



        # Map commands to functions
        command_functions = {
            '/hola': self.activate_chatgpt,
            '/chao': self.deactivate_chatgpt

        }

        # Get the function associated with the received command
        command_function = command_functions.get(received_text)

        if command_function:
            if asyncio.iscoroutinefunction(command_function):
                task = asyncio.create_task(command_function(user_id, message))
                response = await task
            else:
                response = command_function(user_id, message)

        elif user_id in self.chatgpt_active_users:
            #print('ChatGPT activo', user_id)
            # Enviar acción de chat "escribiendo"
            await self.typing_indicator(user_id)
            # Obtener respuesta de OpenAI
            response = self.openai_instance.get_response(conversation_history)
        else:
            #print('ChatGPT desactivado.', user_id)

            await self.typing_indicator(user_id)
            # Process message with spaCy
            user_document = self.db_connection.find_one_documents("users", {"user_id": user_id})
            user_spacy_model = user_document.get("spacy_model", self.spacy_model_name_default) if user_document is not None else self.spacy_model_name_default
            #####
            spacy.prefer_gpu()
            nlp = spacy.load(user_spacy_model)
            doc = nlp(received_text)
            entities = [ent.text for ent in doc.ents]
            nouns = [token.text for token in doc if token.pos_ == "NOUN"]
            adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
            verbs = [token.text for token in doc if token.pos_ == "VERB"]
            adverbs = [token.text for token in doc if token.pos_ == "ADV"]
            pronouns = [token.text for token in doc if token.pos_ == "PRON"]
            prepositions = [token.text for token in doc if token.pos_ == "ADP"]
            conjunctions = [token.text for token in doc if token.pos_ == "CCONJ" or token.pos_ == "SCONJ"]
            # Generate response based on spaCy analysis
            if entities:
                response = f"Veo que mencionaste {', '.join(entities)}. ¿Me puedes contar más sobre eso?"
            elif nouns and adjectives and verbs:
                response = f"Háblame más sobre {', '.join(adjectives)} {nouns[0]} y por qué {verbs[0]} es importante."
            elif nouns and adjectives:
                response = f"Háblame más sobre {', '.join(adjectives)} {nouns[0]}."
            elif adverbs:
                response = f"Me parece interesante lo que me dices. ¿Puedes ser más específico con respecto a {', '.join(adverbs)}?"
            elif pronouns:
                response = f"¿Puedes aclararme a quién te refieres con {', '.join(pronouns)}?"
            elif prepositions:
                response = f"¿Puedes darme más detalles acerca de {', '.join(prepositions)}?"
            elif conjunctions:
                response = f"¿Podrías decirme más acerca de la relación entre las ideas que unen {', '.join(conjunctions)}?"
            else:
                if received_text == "/start":
                    await self.typing_indicator(user_id)
                    response = welcome_message
                if received_text == "/task":
                    await self.typing_indicator(user_id)
                    response = f"📝 ¡Próximamente! Estamos trabajando en la programación de tareas para que puedas ser más productivo/a. ¡Mantente atento/a!"
                else:
                    await self.typing_indicator(user_id)
                    additional_question = "¿Puedes darme más detalles sobre tu pregunta?"
                    response = additional_question



        user_document = self.db_connection.find_one_documents("users", {"user_id": user_id})
        user_spacy_model = user_document.get("spacy_model", self.spacy_model_name_default) if user_document is not None else self.spacy_model_name_default
        # Save the conversation in MongoDB
        conversation = {
            "user_id": user_id,
            "user_username": user_username,
            "user_name": user_first_name,
            "user_last_name": user_last_name,
            "user_message": received_text,
            "bot_message": response,
            "model": user_spacy_model if user_id not in self.chatgpt_active_users else "ChatGPT",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        }
        self.db_connection.insert_one("conversations", conversation)
        # Add ChatGPT's response to the conversation
        self.user_conversations[user_id].append(f"ChatGPT: {response}")
        # Send the response to the chat
        await self.typing_indicator(user_id)
        await message.answer(response)

    async def activate_chatgpt(self, user_id, message):
        # Verificar si el chat ya está activo para el usuario
        user = self.db_connection.find_one_documents("users", {"user_id": user_id})
        if user and user.get("chatgpt_active"):
            await self.typing_indicator(user_id)
            status_message = "¡Genial! ChatGPT está listo y activado para ayudarte. No dudes en hacerme cualquier pregunta, estoy aquí para asistirte. 😊"
            return status_message
        elif user and user.get("banned_gpt"):
            await self.typing_indicator(user_id)
            banned_message = "Lo siento, no puedo activar ChatGPT para ti porque tu acceso ha sido restringido. Por favor, ponte en contacto con el administrador si crees que esto es un error."
            return banned_message
        else:
            # Si el usuario no está activo y no está baneado, actualizar el campo chatgpt_active.
            user_data = {"chatgpt_active": True}
            self.db_connection.update_one("users", {"user_id": user_id}, {"$set": user_data})
            self.chatgpt_active_users[user_id] = True

            # Mensaje de saludo del chatGPT
            await self.typing_indicator(user_id)
            user_first_name = message.from_user.first_name
            activate_message = f"¡Hola {user_first_name}! Soy ChatGPT, tu amigable asistente. Estoy aquí para ayudarte con tus preguntas. Por favor, adelante, pregúntame cualquier cosa y estaré encantado de responder. Cuando quieras despedirte, simplemente escribe /chao."
            return activate_message

    async def deactivate_chatgpt(self, user_id, message):
        # Cambiar el estado de activación del chat a False para el usuario en la base de datos
        self.db_connection.update_one("users", {"user_id": user_id}, {"$set": {"chatgpt_active": False}})
        self.chatgpt_active_users.pop(user_id, None)
        await self.typing_indicator(user_id)
        farewell_message = "¡Gracias por usar mis servicios! Espero haber sido de ayuda. Si necesitas asistencia en el futuro, no dudes en activarme de nuevo. ¡Que tengas un excelente día! 😊"
        return farewell_message

    async def typing_indicator(self, user_id):
        await self.bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)


    async def start(self, message: types.Message):
        # Obtener el primer nombre del usuario del objeto de mensaje
        user_first_name = message.from_user.first_name

        # Construir el mensaje de bienvenida con el nombre del usuario
        welcome_message = f"¡Hola! {user_first_name} Soy un bot de Telegram equipado con ChatGPT y spaCy, un asistente inteligente basado en inteligencia artificial. Para activar ChatGPT, escribe /hola. Si deseas salir, simplemente escribe /chao."

        # Enviar el mensaje de bienvenida al usuario
        await message.answer(welcome_message)
    async def run(self):
        # Método que inicia el polling del bot
        await self.dp.start_polling()
