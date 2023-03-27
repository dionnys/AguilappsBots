#gunicorn webhook:app -w 4 -b 0.0.0.0:8080
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Obtener información del mensaje entrante
    sender = request.form.get('From')
    message_body = request.form.get('Body')

    # Procesar el mensaje entrante (aquí puedes agregar tu lógica personalizada)
    print(f'Mensaje recibido de {sender}: {message_body}')

    # Enviar una respuesta al mensaje entrante
    response = MessagingResponse()
    response.message('Mensaje recibido, gracias!')
    return str(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)