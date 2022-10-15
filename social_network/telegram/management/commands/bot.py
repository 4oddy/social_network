from django.core.management.base import BaseCommand

from ...tg.bot import bot


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('start')

    def handle(self, *args, **options):
        if options['start']:
            bot.infinity_polling()
