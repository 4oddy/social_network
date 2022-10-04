from ..utils import get_current_date


def time(request):
    return {'date': get_current_date()}
