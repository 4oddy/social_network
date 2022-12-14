from django.contrib.auth import get_user_model

User = get_user_model()

Devices = User.Devices


class DeviceExposerMiddleware:
    """ Middleware to get user device """
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if self._is_mobile(request):
                user.device = Devices.MOBILE
            else:
                user.device = Devices.PC

            user.save(update_fields=['device'])

        response = self._get_response(request)
        return response

    @staticmethod
    def _is_mobile(request):
        if request.user_agent.is_mobile or request.user_agent.is_tablet:
            return True
        return False
