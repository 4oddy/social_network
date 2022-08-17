from django.core.exceptions import ValidationError


def custom_username_validator(username):
    if '@' in username:
        raise ValidationError('@ не может быть в имени пользователя')

    if len(username) < 4:
        raise ValidationError('Минимальная длина: 4')

    if len(username) > 50:
        raise ValidationError('Максимальная длина: 50')
