# Generated by Django 4.0.4 on 2023-04-05 21:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Имя')),
                ('date_of_creating', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
            options={
                'verbose_name': 'Беседа',
                'verbose_name_plural': 'Беседы',
            },
        ),
        migrations.CreateModel(
            name='ConservationMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст сообщения')),
                ('date_of_sending', models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')),
            ],
            options={
                'verbose_name': 'Сообщение беседы',
                'verbose_name_plural': 'Сообщения беседы',
                'ordering': ['date_of_sending'],
            },
        ),
        migrations.CreateModel(
            name='Dialog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Имя')),
                ('date_of_creating', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
            options={
                'verbose_name': 'Диалог',
                'verbose_name_plural': 'Диалоги',
            },
        ),
        migrations.CreateModel(
            name='DialogMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст сообщения')),
                ('date_of_sending', models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')),
                ('group', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat_app.dialog', verbose_name='Диалог')),
            ],
            options={
                'verbose_name': 'Сообщение диалога',
                'verbose_name_plural': 'Сообщения диалога',
                'ordering': ['date_of_sending'],
            },
        ),
    ]
