from flask import Flask
from db_config import db, BotModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:toor@localhost/celebrities'
db.init_app(app)


from telegram import *
import telebot
from db_config import BotModel


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        active_bots = BotModel.query.filter_by(status='active').all()
        for bot in active_bots:
            bot_instance = telebot.TeleBot(bot.telegram_token)
            webhook_url = f'https://ef40-2806-2f0-a2c1-e998-4cde-108d-db97-a3e2.ngrok-free.app/webhook/{bot.name}'
            bot_instance.remove_webhook()
            bot_instance.set_webhook(url=webhook_url)
            webhook_info = bot_instance.get_webhook_info()
            print(webhook_info.url)
    app.run()