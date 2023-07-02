import io

import telebot
from flask import jsonify, request
from api_service import ApiService
from db_config import BotModel, MessageModel
from main import app
from instagram import get_posts
import requests

@app.route('/bots', methods=['GET'])
def get_bots():
    user = request.args.get('user')  # Obtener el valor del parámetro de consulta 'status'
    bots = BotModel.query.all()
    bot_data = []

    for bot in bots:
        if user == bot.user:
            bot_info = {
                'name': bot.name,
                'status': bot.status,
                'telegram_token': bot.telegram_token,
                'id': bot.id,
                'instagram': bot.instagram
            }
            bot_data.append(bot_info)

    return jsonify(bot_data)


@app.route('/bots', methods=['POST'])
def create_bot():
    data = request.form
    print(data)
    celebrity_name= data['name']
    botModel = BotModel.get_bot_by_name(celebrity_name)
    if botModel is not None:
        return jsonify({'message': 'Bot ya existe.'})

    bot = BotModel.from_dict(data)
    bot.save()

    audio_file = request.files['audio']
    print(audio_file)
    url = 'https://api.elevenlabs.io/v1/voices/add'
    headers = {
        'accept': 'application/json',
        'xi-api-key': '126cb71a0e2dba4e5402ac3e47625b68'
    }
    requestBody = {
        'name': celebrity_name,
        'description': celebrity_name,
    }
    files = {
        'files': (audio_file.filename, audio_file.stream, audio_file.content_type)
    }
    response = requests.post(url, headers=headers, data=requestBody, files=files)

    if response.status_code == 200:
        response_data = response.json()
        voice = response_data['voice_id']
        print(voice)
        BotModel.update_voice_id(bot, voice)
        BotModel.update_status(bot, 'active')
        bot_instance = telebot.TeleBot(data['telegram_token'])
        webhook_url = f'https://51fc-2806-2f0-a2c1-e998-75ed-efdb-98ce-8d3e.ngrok-free.app/webhook/{celebrity_name}'
        bot_instance.remove_webhook()
        bot_instance.set_webhook(url=webhook_url)
        webhook_info = bot_instance.get_webhook_info()
        print(webhook_info.url)
        return jsonify({'message': 'Bot creado exitosamente.'})
    else:
        return jsonify({'message': 'Error en la llamada a la API.'}), response.status_code


@app.route('/disable_bot/<int:bot_id>', methods=['PUT'])
def disable_bot(bot_id):
        bot_data = BotModel.get_bot_by_id(bot_id)
        if bot_data:
            bot_data.update_status('inactive')
            return jsonify({'message': 'Bot desactivado exitosamente.'})
        else:
            return jsonify({'message': 'Bot no encontrado.'}), 404


@app.route('/enable_bot/<int:bot_id>', methods=['PUT'])
def enable_bot(bot_id):
        bot_data = BotModel.get_bot_by_id(bot_id)
        if bot_data:
            bot_data.update_status('active')
            return jsonify({'message': 'Bot desactivado exitosamente.'})
        else:
            return jsonify({'message': 'Bot no encontrado.'}), 404

@app.route('/webhook/<bot_name>', methods=['POST'])
def dynamic_webhook(bot_name):
    bot_data = BotModel.get_bot_by_name(bot_name)
    if bot_data:
        if bot_data.status == 'active':
            celebrity_bot = telebot.TeleBot(bot_data.telegram_token)
            req_data = request.get_json(force=True)
            username = req_data['message']['from']['username']
            update = telebot.types.Update.de_json(request.get_json(force=True))
            handle_telegram_message(celebrity_bot, update.message, bot_data,username)
            return 'OK'
        else:
            return 'Bot inactive', 204
    else:
        return 'Bot no encontrado', 204


@app.route('/instagram/', methods=['GET'])
def post():
    active_bots = BotModel.query.filter_by(status='active').all()
    for bot in active_bots:
        get_posts(bot.name)

    return jsonify({'message': 'Listo'}), 200

def handle_telegram_message(celebrity_bot, message, bot_data, username):
    if message is None:
        return

    user_id = message.chat.id
    text = message.text
    fans_name = message.from_user.first_name
    is_group = message.chat.type
    if is_group == "supergroup":
        validate = ApiService.validate(text)
        if bot_data.group_id is None:
            print("change group id")
            BotModel.update_group_id(bot_data, user_id)
    else:
        validate = "Y"
    if validate == "Y":
        response, msg = ApiService.generate_response(user_id,fans_name, text, bot_data,username)
        if isinstance(response, io.BytesIO):
            audio_bytes = response.getvalue()
            celebrity_bot.send_audio(user_id, audio_bytes)
        else:
            celebrity_bot.send_message(user_id, response)

        #save chat
        chat_instance = MessageModel()
        chat_instance.user = text
        chat_instance.bot = msg
        chat_instance.username = username
        chat_instance.save()

