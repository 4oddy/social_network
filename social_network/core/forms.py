from captcha.fields import CaptchaField
from django import forms
from django.conf import settings

captcha_text = 'Подтвердите, что вы не робот'


class BaseForm(forms.ModelForm):
    """ Form with captcha if it's not debug mode """
    if not settings.DEBUG:
        simple_captcha = CaptchaField(label=captcha_text)
