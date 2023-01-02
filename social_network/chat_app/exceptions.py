from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException

User = get_user_model()


class NotInFriendsError(APIException):
    """ Error occurs when somebody tries to create group with people not in friendship """
    status_code = 400
    default_code = 'not_in_friends'

    def __init__(self, not_in_friends):
        self.default_detail = {'not_in_friends': not_in_friends}
        super().__init__()


class DialogExistsError(APIException):
    """ Error occurs when the same dialog exists """
    status_code = 400
    default_detail = 'Такой диалог уже существует'
    default_code = 'dialog_exists'


class SelfDialogError(APIException):
    """ Error occurs when user tries to create dialog with himself """
    status_code = 400
    default_detail = 'Нельзя создать диалог с самим собой'
    default_code = 'self_dialog'
