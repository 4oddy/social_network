from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException

User = get_user_model()


class NotInFriendsException(APIException):
    status_code = 400
    default_code = 'not_in_friends'

    def __init__(self, not_in_friends):
        self.default_detail = {'not_in_friends': not_in_friends}
        super().__init__()


class DialogExistsException(APIException):
    status_code = 400
    default_code = 'dialog_exists'
    default_detail = 'Такой диалог уже существует'
