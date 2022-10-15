from dotenv import load_dotenv

from django.conf import settings

import telebot
import os

load_dotenv(settings.BASE_DIR / 'test.env')


def bot_connect() -> telebot.TeleBot:
    token = os.environ.get('token')
    bot = telebot.TeleBot(token=token)
    return bot


tg_bot = bot_connect()
