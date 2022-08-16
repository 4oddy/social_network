import os

from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


def get_current_date():
    return datetime.now().strftime('%d.%m.%Y %H:%M:%S')


def clean_images():
    path = 'images\\user_images\\'

    users = User.objects.all()

    using = []

    for user in users:
        user_img = user.image.name.split('/')[-1]
        if user_img in os.listdir(path):
            using.append(user_img)

    for img in os.listdir(path):
        if img not in using:
            os.remove(img)
