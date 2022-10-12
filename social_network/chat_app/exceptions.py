class SelfDialogCreated(Exception):
    """ Exception generates when user tries to create dialog with himself """
    pass


class UserNotInGroup(Exception):
    pass


class UserNotInConservation(UserNotInGroup):
    """ Exception generates when user not in conservation in which tries to send message """
    pass


class UserNotInDialog(UserNotInGroup):
    """ Exception generates when user not in dialog in which tries to send message """
    pass
