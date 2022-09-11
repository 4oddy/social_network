from chat_app import models


class RequestExposer:
    """ Middleware to get current request for getting companion of user (in models.Dialog) """
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        # setting current request
        models.exposed_request = request

        response = self._get_response(request)

        return response
