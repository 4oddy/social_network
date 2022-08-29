from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import FriendRequest
from .utils import get_current_date
from .tasks import send_email

User = get_user_model()


def find_users(username):
    queryset = User.objects.filter(username__icontains=username)
    return queryset


def find_friend_request(first_user, second_user):
    queryset = FriendRequest.objects.filter(Q(from_user=first_user) & Q(to_user=second_user) |
                                            Q(from_user=second_user) | Q(to_user=first_user)).first()
    return queryset


# func to get data from hidden form's fields
def get_data_for_action(request):
    user_path = request.POST['current_path']
    from_user_id = request.user.pk
    from_user = request.user
    to_user_id = request.POST['user_id']

    return {'user_path': user_path, 'from_user_id': from_user_id, 'from_user': from_user,
            'to_user_id': to_user_id}


def get_username_from_kwargs(kwargs):
    return kwargs['username'].replace('@', '')


def create_friend_request(from_user, to_user_id):
    request = FriendRequest.objects.create(from_user=from_user, to_user_id=to_user_id)

    if settings.SEND_EMAILS:
        to_user = get_object_or_404(User, pk=to_user_id)
        name = to_user.first_name

        if not name:
            name = to_user.username

        username = from_user.username

        email_body = settings.DEFAULT_EMAIL_FRIEND_REQUEST_BODY.format(name=name, name_requested=username,
                                                                       date=get_current_date())

        send_email.delay(subject=settings.DEFAULT_EMAIL_FRIEND_REQUEST_SUBJECT, body=email_body, to=[to_user.email])

    return request


def send_email_login(user):
    if settings.SEND_EMAILS:
        name = user.first_name
        username = user.username

        if not name:
            name = user.username

        email_body = settings.DEFAULT_EMAIL_LOGIN_BODY.format(name=name, username=username, date=get_current_date())

        send_email.delay(subject=settings.DEFAULT_EMAIL_LOGIN_SUBJECT, body=email_body, to=[user.email])


def send_email_changed_settings(user):
    if settings.SEND_EMAILS:
        name = user.first_name

        if not name:
            name = user.username

        email_body = settings.DEFAULT_EMAIL_SETTINGS_CHANGED_BODY.format(name=name, date=get_current_date())

        send_email.delay(subject=settings.DEFAULT_EMAIL_SETTINGS_CHANGED_SUBJECT, body=email_body, to=[user.email])


def delete_from_friendship(first, second):
    request = find_friend_request(first, second)

    if first in second.friends.all() and second in first.friends.all():
        first.friends.remove(second)
        second.friends.remove(first)

    request.delete() if request else None
