from flask import Flask
from db_config import db, BotModel
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:toor@localhost/celebrities'
db.init_app(app)
scheduler = APScheduler()



from telegram import *
import telebot
from db_config import BotModel

def scheduleTask():
    # Code to be executed every minute
    from instagram import get_posts
    get_posts('shakira')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        active_bots = BotModel.query.filter_by(status='active').all()
        for bot in active_bots:
            bot_instance = telebot.TeleBot(bot.telegram_token)
            webhook_url = f'https://94dc-213-173-36-165.ngrok-free.app/webhook/{bot.name}'
            bot_instance.remove_webhook()
            bot_instance.set_webhook(url=webhook_url)
            webhook_info = bot_instance.get_webhook_info()
            print(webhook_info.url)

        #scheduler.add_job(id = 'Scheduled Task', func=scheduleTask, trigger="interval", seconds=40)
        #scheduler.start()
    app.run(port=8080)