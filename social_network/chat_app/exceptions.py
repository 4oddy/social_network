from core.exceptions import ApplicationError


class NotInFriendsError(ApplicationError):
    """ Error occurs when somebody tries to create group with people not in friendship """
    @property
    def default_error_message(self) -> str:
        return 'Не в друзьях'


class DialogExistsError(ApplicationError):
    """ Error occurs when the same dialog exists """
    @property
    def default_error_message(self) -> str:
        return 'Такой диалог уже существует'


class SelfDialogError(ApplicationError):
    """ Error occurs when user tries to create dialog with himself """
    @property
    def default_error_message(self) -> str:
        return 'Нельзя начать диалог с самим собой'
