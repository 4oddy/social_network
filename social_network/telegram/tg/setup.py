import os

import telebot
from django.conf import settings
from dotenv import load_dotenv

load_dotenv(settings.BASE_DIR / 'test.env')


def bot_connect() -> telebot.TeleBot:
    token = os.environ.get('token')
    bot = telebot.TeleBot(token=token)
    return bot


tg_bot = bot_connect()
