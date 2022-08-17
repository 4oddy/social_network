from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from captcha.fields import CaptchaField

from .models import CustomUser, Post
from .validators import custom_username_validator

User = get_user_model()

captcha_text = 'Подтвердите, что вы не робот'


class FindUserForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150)


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', max_length=50, min_length=4,
                               validators=[custom_username_validator])
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    image = forms.ImageField(label='Фото профиля', required=False)

    simple_captcha = CaptchaField(label=captcha_text)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'image', 'first_name', 'last_name', 'password1', 'password2', 'simple_captcha')


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(label='Логин или Email', widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": (
            "Неверный логин или пароль"
        ),
        "inactive": ("Аккаунт неактивен", ),
    }


class UserSettingsForm(forms.ModelForm):
    image = forms.ImageField(label='Фото профиля', widget=forms.FileInput)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'image')


class PostCreatingForm(forms.ModelForm):
    simple_captcha = CaptchaField(label=captcha_text)

    class Meta:
        model = Post
        fields = ('title', 'description', 'simple_captcha')
