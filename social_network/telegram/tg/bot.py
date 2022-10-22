from .setup import tg_bot as bot
from .authentication.base import TelegramAuthentication

TelegramAuthentication.set_bot(bot)

auth_system = TelegramAuthentication()


def hello(message):
    bot.reply_to(message, 'Hello')


@bot.message_handler(commands=['help'], func=hello)
@auth_system.basic_authentication
def welcome(message):
    pass


@bot.message_handler(commands=['sending_notifies'])
@auth_system.basic_authentication
def switch_sending_emails(message, user):
    sending = user.switch_sending_emails()
    bot.reply_to(message, 'Уведомления {mode}'.format(mode='включены' if sending else 'выключены'))
