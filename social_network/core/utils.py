from datetime import datetime
from uuid import uuid4

from django.contrib.auth import get_user_model

User = get_user_model()


def get_current_date():
    return datetime.now().strftime('%d.%m.%Y %H:%M:%S')


def generate_user_data():
    username = f'test{uuid4()}'
    email = username + '@mail.ru'
    return {'username': username, 'password': username, 'email': email}
