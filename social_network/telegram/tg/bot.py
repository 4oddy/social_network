from django.contrib.auth import get_user_model

from telegram.tg.tokens import generate_authentication_token

from .authentication.base import TelegramAuthentication
from .setup import tg_bot as bot

auth_system = TelegramAuthentication(bot=bot)

auth_system.add_command('sending_notifies', 'вкл./выкл. уведомления')

User = get_user_model()


@bot.message_handler(commands=['sending_notifies'])
@auth_system.basic_authentication
def switch_sending_emails(message, user):
    sending = user.switch_sending_emails()
    response = 'Уведомления {}'.format('включены' if sending else
                                       'выключены')
    bot.reply_to(message, response)


@bot.message_handler(commands=['generate'])
def generate_token(message):
    username = message.text.split()[1]
    user = User.objects.get(username=username)
    token = generate_authentication_token(user)
    bot.reply_to(message, token)
