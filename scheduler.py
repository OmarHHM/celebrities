from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from instagram import get_posts
from db_config import BotModel


def job():
    active_bots = BotModel.query.filter_by(status='active').all()
    for bot in active_bots:
        if bot.group_id is not None:
            instagram_username = bot.instagram.replace("@", "")
            print(f"""Ejecutando tarea programada {instagram_username}""")
            get_posts(instagram_username)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'cron', hour=8, minute=45)
    scheduler.start()
