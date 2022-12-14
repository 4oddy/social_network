from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.utils import timezone

from main_app.services import send_email_login

User = get_user_model()


class CustomBackend(BaseBackend):
    """ Custom Authentication logic to sign in by email or username """
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.save(update_fields=['last_online'])
            return user
        except User.DoesNotExist:
            return None

    def authenticate(self, request, **kwargs):
        username = kwargs['username']
        password = kwargs['password']

        try:
            # checking by email
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                # by username
                user = User.objects.get(username=username)

            if user.check_password(password) is True:
                user.last_online = timezone.now()
                send_email_login(user)
                return user
            return None

        except User.DoesNotExist:
            return None
