import io

import telebot
from flask import Flask, request
from api_service import ApiService

app = Flask(__name__)


bot = telebot.TeleBot('')


@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))


    handle_telegram_message(update.message)

    return 'OK'


def handle_telegram_message(message):
    print(message)
    if message is None:
        return

    user_id = message.chat.id
    text = message.text
    fans_name = message.from_user.first_name
    print(fans_name)
    is_group = message.chat.type
    if is_group == "supergroup":
        validate = ApiService.validate(text)
    else:
        validate = "Y"
    if validate == "Y":
        response = ApiService.generate_response(user_id,fans_name, text)
        if isinstance(response, io.BytesIO):
            audio_bytes = response.getvalue()
            bot.send_audio(user_id, audio_bytes)
        else:
            bot.send_message(user_id, response)

# Iniciar el bot de Telegram
bot.remove_webhook()
bot.set_webhook(url='https://cb78-2806-2f0-a2c1-e998-4cde-108d-db97-a3e2.ngrok-free.app/telegram_webhook')


if __name__ == '__main__':
    app.run()