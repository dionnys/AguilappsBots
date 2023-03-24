class SaimeNotificationHandler:
    def __init__(self, chatgpt_active_users, bot):
        self.chatgpt_active_users = chatgpt_active_users
        self.bot = bot

    async def handle_message(self, message, received_text, user_id):
        # Check if ChatGPT is inactive and the message contains the keyword 'avísame' and 'Saime'
        if user_id not in self.chatgpt_active_users and 'avísame' in received_text and 'saime' in received_text:
            await self.typing_indicator(user_id)
            await message.answer('¡Entendido! Por favor, proporciona los siguientes datos:')

            # Ask the user for the necessary data to create the scheduled task
            await message.answer('Ingresa la URL a la que deseas acceder:')
            url = await self.bot.wait_for('message', timeout=120)
            url = url.text

            await message.answer('Ingrese la fecha y hora de la notificación en el siguiente formato: yyyy-mm-dd hh:mm:ss')
            notification_date = await self.bot.wait_for('message', timeout=120)
            notification_date = notification_date.text

            await message.answer('¿Cómo deseas ser notificado? Ingresa "email" o "número de teléfono".')
            notification_method = await self.bot.wait_for('message', timeout=120)
            notification_method = notification_method.text.lower()

            # Check if the notification method is valid
            while notification_method not in ('email', 'número de teléfono'):
                await message.answer('Por favor, ingresa un método de notificación válido: "email" o "número de teléfono".')
                notification_method = await self.bot.wait_for('message', timeout=120)
                notification_method = notification_method.text.lower()

            # Ask the user for their email or phone number
            if notification_method == 'email':
                await message.answer('Ingresa tu dirección de correo electrónico:')
                notification_email = await self.bot.wait_for('message', timeout=120)
                notification_email = notification_email.text
                notification_number = None
            else:
                await message.answer('Ingresa tu número de teléfono (con código de área):')
                notification_number = await self.bot.wait_for('message', timeout=120)
                notification_number = notification_number.text
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
            await self.create_scheduled_task(**task_data)
            await message.answer('¡Genial! La tarea programada ha sido creada.')
