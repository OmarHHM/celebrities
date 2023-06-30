import io

import telebot
from flask import jsonify, request
from api_service import ApiService
from db_config import BotModel
from main import app

@app.route('/bots', methods=['GET'])
def get_bots():
    bots = BotModel.query.all()
    bot_data = []

    for bot in bots:
        bot_info = {
            'name': bot.name,
            'active': bot.status == 'active'
        }
        bot_data.append(bot_info)

    return jsonify(bot_data)
@app.route('/bots', methods=['POST'])
def create_bot():
    data = request.get_json()
    bot = BotModel.from_dict(data)
    bot.save()
    return jsonify({'message': 'Bot creado exitosamente.'})

@app.route('/disable_bot/<int:bot_id>', methods=['PUT'])
def disable_bot(bot_id):
        bot_data = BotModel.get_bot_by_id(bot_id)
        if bot_data:
            bot = BotModel.from_dict(bot_data)
            bot.update_status('inactive')
            return jsonify({'message': 'Bot desactivado exitosamente.'})
        else:
            return jsonify({'message': 'Bot no encontrado.'}), 404
        
@app.route('/enable_bot/<int:bot_id>', methods=['PUT'])
def disable_bot(bot_id):
        bot_data = BotModel.get_bot_by_id(bot_id)
        if bot_data:
            bot = BotModel.from_dict(bot_data)
            bot.update_status('active')
            return jsonify({'message': 'Bot desactivado exitosamente.'})
        else:
            return jsonify({'message': 'Bot no encontrado.'}), 404

@app.route('/webhook/<bot_name>', methods=['POST'])
def dynamic_webhook(bot_name):
    bot_data = BotModel.get_bot_by_name(bot_name)
    if bot_data:
        if bot_data.status == 'active':
            celebrity_bot = telebot.TeleBot(bot_data.telegram_token)
            update = telebot.types.Update.de_json(request.get_json(force=True))
            print(update.message)
            handle_telegram_message(celebrity_bot, update.message, bot_data)
            return 'OK'
        else:
            return 'Bot inactive', 204
    else:
        return 'Bot no encontrado', 204


def handle_telegram_message(celebrity_bot, message, bot_data):
    print(message)
    if message is None:
        return

    user_id = message.chat.id
    text = message.text
    fans_name = message.from_user.first_name
    is_group = message.chat.type
    if is_group == "supergroup":
        validate = ApiService.validate(text)
    else:
        validate = "Y"
    if validate == "Y":
        response = ApiService.generate_response(user_id,fans_name, text, bot_data)
        if isinstance(response, io.BytesIO):
            audio_bytes = response.getvalue()
            celebrity_bot.send_audio(user_id, audio_bytes)
        else:
            celebrity_bot.send_message(user_id, response)

