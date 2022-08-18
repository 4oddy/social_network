from django import forms
from django.conf import settings

from captcha.fields import CaptchaField

captcha_text = 'Подтвердите, что вы не робот'


class BaseForm(forms.ModelForm):
    if not settings.DEBUG:
        simple_captcha = CaptchaField(label=captcha_text)
