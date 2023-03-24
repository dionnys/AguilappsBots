from datetime import datetime
import validators
import re


class TaskHandler:
    def __init__(self, bot, task_manager):

        self.bot = bot
        self.task_manager = task_manager

    async def handle_message(self, message, received_text, user_id):
        # Check if ChatGPT is inactive and the message contains the keyword 'schedule'
        if 'schedule' in received_text:
            await self.typing_indicator(user_id)
            await message.answer('Entendido. Por favor, proporcione los siguientes detalles:')

            # Ask the user for the necessary data to create the scheduled task
            await message.answer('Ingrese la URL a la que desea acceder:')
            url = await self.get_valid_input(message, self.is_valid_url)
            url = url.lower()

            await message.answer('Ingrese la fecha y hora de la notificación en el siguiente formato: yyyy-mm-dd hh:mm:ss')
            notification_date = await self.get_valid_input(message, self.is_valid_date)
            notification_date = notification_date.lower()

            await message.answer('¿Cómo desea recibir la notificación? Ingrese "correo electrónico" o "número de teléfono".')
            notification_method = await self.get_valid_input(message, self.is_valid_notification_method)
            notification_method = notification_method.lower()

            # Check if the notification method is valid
            while notification_method not in ('correo electrónico', 'número de teléfono'):
                await message.answer('Ingrese un método de notificación válido: "correo electrónico" o "número de teléfono".')
                notification_method = await self.get_valid_input(message, self.is_valid_notification_method)
                notification_method = notification_method.lower()

            # Ask the user for their email or phone number
            if notification_method == 'correo electrónico':
                await message.answer('Ingrese su dirección de correo electrónico:')
                notification_email = await self.get_valid_input(message, self.is_valid_email)
                notification_email = notification_email.lower()
                notification_number = None
            else:
                await message.answer('Ingrese su número de teléfono (con formato 123-456-7890):')
                notification_number = await self.get_valid_input(message, self.is_valid_phone_number)
                notification_email = None

            # Create the scheduled task
            task_data = {
                'user_id': user_id,
                'url': url,
                'notification_date': notification_date,
                'notification_method': notification_method,
                'notification_email': notification_email,
                'notification_number': notification_number
            }
            self.task_manager.create_task(**task_data)
            await message.answer('¡Genial! La tarea programada ha sido creada.')

    async def get_valid_input(self, message, validator):
        while True:
            user_input = await self.bot.wait_for('message', timeout=120)
            user_input = user_input.text.strip()
            if validator(user_input):
                return user_input
            else:
                await message.answer('Entrada no válida. Inténtelo de nuevo.')

def is_valid_date(self, date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False
