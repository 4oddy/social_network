from .setup import tg_bot as bot
from .authentication.base import TelegramAuthentication

TelegramAuthentication.set_bot(bot)

auth_system = TelegramAuthentication()


@bot.message_handler(commands=['start'])
@auth_system.basic_authentication
def welcome(message):
    bot.reply_to(message, 'Hello')
