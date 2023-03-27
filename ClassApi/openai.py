import openai
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

class OpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.name = name
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stop = stop
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
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