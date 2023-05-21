import openai
import whisper
from ConnectionDao.mongodb_connection import MongoDBConnection


openai_setting = MongoDBConnection.find_documents('setting')
for configs in openai_setting:
    engine  = configs['openai_setting']['engine']
    name = configs['openai_setting']['name']
    temperature = configs['openai_setting']['temperature']
    max_tokens = configs['openai_setting']['max_tokens']
    stop = configs['openai_setting']['stop']
    top_p = configs['openai_setting']['top_p']
    frequency_penalty = configs['openai_setting']['frequency_penalty']
    presence_penalty = configs['openai_setting']['presence_penalty']
    size = configs['openai_setting']['generate_image']['size']
    nro_image = configs['openai_setting']['generate_image']['nro_image']
    whisper_model=configs['openai_setting']['whisper_model']

class OpenAI:
    def __init__(self, api_key):
        self.api_key=api_key
        self.name=name
        self.engine=engine
        self.temperature=temperature
        self.max_tokens=max_tokens
        self.stop=stop
        self.top_p=top_p
        self.frequency_penalty=frequency_penalty
        self.presence_penalty=presence_penalty
        self.size=size
        self.nro_image=nro_image
        self.whisper_model=whisper_model

        openai.api_key = api_key
        print(self.engine)

    def get_response(self, question):

        if self.engine == "gpt-3.5-turbo":
            completion = openai.ChatCompletion.create(
            model=self.engine,
            messages=[{"role": "user", "content": question}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=self.stop,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty
            )
            response = (completion.choices[0].message["content"])

        else:
            completion = openai.Completion.create(
                engine=self.engine,
                prompt=f"User: {question}\n{self.name}:",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=self.stop,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
            response = completion.choices[0].text.strip()

        return response


    def generate_image(self, question):
        response = openai.Image.create(
            prompt = question,
            n = self.nro_image,
            size = self.size
        )
        image_urls = [data['url'] for data in response['data']]
        image_urls_str = ', '.join(image_urls) # Unir las URL de las imágenes con comas
        clean_image_urls_str = image_urls_str.replace('[', '').replace(']', '').replace('\'', '')
        return clean_image_urls_str


    def transcribe_speech(self, audio_file_path):
        modelo = whisper.load_model(self.whisper_model)

        # Cargar el audio y ajustarlo para que tenga una duración de 30 segundos
        audio = whisper.load_audio(audio_file_path)
        audio = whisper.pad_or_trim(audio)

        # Crear un log-Mel espectrograma y moverlo al mismo dispositivo que el modelo
        mel = whisper.log_mel_spectrogram(audio).to(modelo.device)

        # Decodificar el audio
        opciones = whisper.DecodingOptions()
        resultado = whisper.decode(modelo, mel, opciones)

        # Devolver el texto reconocido
        return resultado.text