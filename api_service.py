import openai
import requests
import io


openai.api_key = ''


class ApiService:
    MAX_VOICE_CALLS = 2
    conversations = {}

    @classmethod
    def get_response_openAI(cls, promp):
        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=promp,
            max_tokens=200,
            temperature=0.1,
            stop=None,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
        )
        generate_response = response.choices[0].text.strip()
        return generate_response

    @classmethod
    def validate(cls, request):
        promp: str = f"""Validate if the following message is directed to Shakira or if it contains the word @onealdeaBot.
        If so, return Y; otherwise, return N. Message = {request}"""
        return cls.get_response_openAI(promp)
    @classmethod
    def texto_to_voice(cls, response_chatgpt):
        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/c4jQUZkogUxtzx3Vbl5l"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": "126cb71a0e2dba4e5402ac3e47625b68"
        }

        data = {
            "text": response_chatgpt,
            "model_id": "eleven_multilingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers)
        audio_bytes = io.BytesIO()

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                audio_bytes.write(chunk)

        audio_bytes.seek(0)  # Reiniciamos el puntero del flujo de bytes al principio
        return audio_bytes


    @classmethod
    def generate_response(cls, user_id, fan_name, request):
        promp: str = f"""Eres la cantante Shakira y atenderás a tus fans, 
        no respondas a los insultos y responde siempre de manera amable, 
        no te inventes nada y dirigite a tu fan por su nombre. 
        Este es el mensaje de {fan_name} : {request}"""
        response = cls.get_response_openAI(promp)
        if user_id not in cls.conversations:
            cls.conversations[user_id] = 0
            return cls.texto_to_voice(response)


        return response