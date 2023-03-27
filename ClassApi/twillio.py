import os
from twilio.rest import Client

class WhatsAppTwilio:
    def __init__(self, account_sid, auth_token):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.client = Client(account_sid, auth_token)

    def send_message(self, from_whatsapp_number, to_whatsapp_number, message_body):
        message = self.client.messages.create(
            from_=f'whatsapp:{from_whatsapp_number}',
            body=message_body,
            to=f'whatsapp:{to_whatsapp_number}'
        )
        return message.sid

if __name__ == "__main__":
    account_sid = ''
    auth_token = ''
    from_whatsapp_number = ''
    to_whatsapp_number = ''

    whatsapp_client = WhatsAppTwilio(account_sid, auth_token)

    # Enviar un mensaje de recordatorio de cita
    message_body = 'Your appointment is coming up on July 21 at 3PM'
    print(whatsapp_client.send_message(from_whatsapp_number, to_whatsapp_number, message_body))

    # Enviar un mensaje de confirmación de pedido
    message_body = 'Your Yummy Cupcakes Company order of 1 dozen frosted cupcakes has shipped and should be delivered on July 10, 2019. Details: http://www.yummycupcakes.com/'
    print(whatsapp_client.send_message(from_whatsapp_number, to_whatsapp_number, message_body))

    # Enviar un mensaje con un código de verificación
    message_body = 'Your Twilio code is 1238432'
    print(whatsapp_client.send_message(from_whatsapp_number, to_whatsapp_number, message_body))
