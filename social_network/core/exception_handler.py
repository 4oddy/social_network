from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import ApplicationError


def custom_exception_handler(exc, context):
    """ Custom DRF exception handler for business logic errors """
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, ApplicationError):
            data = {
                "message": exc.message,
            }

            if exc.extra:
                data.update({'extra': exc.extra})

            response = Response(data, status=400)

    return response
