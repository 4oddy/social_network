class DeviceExposerMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if self._is_mobile(request):
                request.user.device = request.user.Devices.MOBILE
            else:
                request.user.device = request.user.Devices.PC

            request.user.save()

        response = self._get_response(request)
        return response

    @staticmethod
    def _is_mobile(request):
        if request.user_agent.is_mobile or request.user_agent.is_tablet:
            return True
        return False
