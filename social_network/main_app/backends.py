from django.utils import timezone
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomBackend(BaseBackend):
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

            # setting last online
            if user.check_password(password) is True:
                user.last_online = timezone.now()
                return user
            return None

        except User.DoesNotExist:
            return None
