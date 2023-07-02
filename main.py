from flask import Flask
from db_config import db, BotModel
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://django:Y7ak6FDm7v@localhost/celebrities'
db.init_app(app)
CORS(app)



from telegram import *
import telebot
from db_config import BotModel
from scheduler import start_scheduler
from flask_apscheduler import APScheduler
from scheduler  import job

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@scheduler.task('interval', id='do_job_1', seconds=60)
def job1():
    with scheduler.app.app_context():
        job()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        active_bots = BotModel.query.filter_by(status='active').all()
        for bot in active_bots:
            bot_instance = telebot.TeleBot(bot.telegram_token)
            webhook_url = f'https://51fc-2806-2f0-a2c1-e998-75ed-efdb-98ce-8d3e.ngrok-free.app/webhook/{bot.name}'
            bot_instance.remove_webhook()
            bot_instance.set_webhook(url=webhook_url)
            webhook_info = bot_instance.get_webhook_info()
            print(webhook_info.url)

    start_scheduler()
    app.run(port=8080)