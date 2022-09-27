from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordResetForm

from .models import CustomUser, Post, Comment
from .validators import custom_username_validator
from .tasks import send_password_reset_email
from core.forms import BaseForm


class FindUserForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150)


class CustomUserCreationForm(UserCreationForm, BaseForm):
    username = forms.CharField(label='Имя пользователя', max_length=50, min_length=4,
                               validators=[custom_username_validator])
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    image = forms.ImageField(label='Фото профиля', required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'image', 'first_name', 'last_name', 'password1', 'password2')


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


class PostCreatingForm(BaseForm):
    class Meta:
        model = Post
        fields = ('title', 'description')


class PostEditingForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description')


class CustomPasswordResetForm(PasswordResetForm):
    """ Form to send password reset emails by Celery worker """
    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Email'
        }
    ))

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        context['user'] = context['user'].id

        send_password_reset_email.delay(subject_template_name=subject_template_name,
                                        email_template_name=email_template_name,
                                        context=context, from_email=from_email, to_email=to_email,
                                        html_email_template_name=html_email_template_name)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
