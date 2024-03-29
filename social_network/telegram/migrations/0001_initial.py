# Generated by Django 4.0.4 on 2023-04-05 21:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.IntegerField(verbose_name='ID')),
                ('send_emails', models.BooleanField(default=True, verbose_name='Отправлять сообщения')),
                ('account', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telegram_profile', to=settings.AUTH_USER_MODEL, verbose_name='Аккаунт')),
            ],
            options={
                'verbose_name': 'Telegram пользователь',
                'verbose_name_plural': 'Telegram пользователи',
            },
        ),
    ]
