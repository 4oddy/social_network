from .authentication.base import TelegramAuthentication
from .setup import tg_bot as bot

auth_system = TelegramAuthentication(bot=bot)


@bot.message_handler(commands=['sending_notifies'])
@auth_system.basic_authentication
def switch_sending_emails(message, user):
    sending = user.switch_sending_emails()
    bot.reply_to(message, 'Уведомления {mode}'.format(mode='включены' if sending else 'выключены'))
