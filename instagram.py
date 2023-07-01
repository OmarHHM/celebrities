import instaloader
from db_config import BotModel
import telebot
from io import BytesIO
import glob
import re


def read_file_by_extension(exten, folder):

    files = glob.glob(f'{folder}/*.{exten}')
    # Iterate over the list of file paths & remove each file.
    file_contents = None

    if files:
        with open(files[0], 'rb') as f:
            file_contents = f.read()

    return file_contents
                
        

def get_posts(username):
    loader = instaloader.Instaloader()
    bot_data = BotModel.get_bot_by_name(username)
    celebrity_bot = telebot.TeleBot(bot_data.telegram_token)
    print("entre")
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        for post in profile.get_posts():

            if post.is_video:
                loader.download_post(post, target=username)
                video_file = read_file_by_extension('mp4', username)
                caption_file = read_file_by_extension('txt', username)
                bytes_io = BytesIO(video_file)
                video_bytes = bytes_io.getvalue()
                celebrity_bot.send_video(-1001923653918, video_bytes, caption=caption_file)
                break
            else:
                print(f"El último post de {username} no es un video.")

    except instaloader.exceptions.ProfileNotExistsException:
        print(f"El perfil '{username}' no existe.")