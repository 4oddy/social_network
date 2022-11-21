from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from typing import Callable

from .models import FriendRequest
from .tasks import send_email

from core.utils import get_current_date


User = get_user_model()


def send_emails(function: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> None:
        if settings.SEND_EMAILS:
            function(*args, **kwargs)
    return wrapper


def find_users(username: str) -> QuerySet:
    queryset = User.objects.filter(username__icontains=username)
    return queryset


def get_request_info(first_user: User, second_user: User) -> dict:
    info = dict()

    request = FriendRequest.objects.filter(from_user=first_user, to_user=second_user).first()

    if request and request.request_status in (request.RequestStatuses.CREATED, request.RequestStatuses.DENIED):
        # you have already created friend request
        info['already_requested'] = True
        info['request_status'] = request.request_status
    else:
        request = FriendRequest.objects.filter(from_user=second_user, to_user=first_user).first()

        if request and request.request_status != request.RequestStatuses.ACCEPTED:
            # user requested to you
            info['requested_to_you'] = True

    return info


def get_user_for_view(from_user: User, to_user_username: str) -> User:
    own_profile = from_user.username == to_user_username

    if own_profile:
        user = from_user
    else:
        user = get_object_or_404(User.objects.prefetch_related('friends'), username=to_user_username)

    return user


# func to get data from hidden form's fields
def get_data_for_action(request: HttpRequest) -> dict:
    user_path = request.POST['current_path']
    from_user = request.user
    to_user_id = request.POST['user_id']
    return {'user_path': user_path, 'from_user': from_user, 'to_user_id': to_user_id}


def get_username_from_kwargs(kwargs: dict) -> str:
    return kwargs['username'].replace('@', '')


@send_emails
def send_friend_request_email(from_user: User, to_user: User) -> None:
    email_body = settings.DEFAULT_EMAIL_FRIEND_REQUEST_BODY.format(name=to_user.get_name(),
                                                                   name_requested=from_user.username,
                                                                   date=get_current_date())

    send_email.delay(subject=settings.DEFAULT_EMAIL_FRIEND_REQUEST_SUBJECT, body=email_body, to=to_user.id)


@send_emails
def send_email_login(user: User) -> None:
    name = user.get_name()
    username = user.username
    email_body = settings.DEFAULT_EMAIL_LOGIN_BODY.format(name=name, username=username, date=get_current_date())
    send_email.delay(subject=settings.DEFAULT_EMAIL_LOGIN_SUBJECT, body=email_body, to=user.id)


@send_emails
def send_email_changed_settings(user: User) -> None:
    name = user.get_name()
    email_body = settings.DEFAULT_EMAIL_SETTINGS_CHANGED_BODY.format(name=name, date=get_current_date())
    send_email.delay(subject=settings.DEFAULT_EMAIL_SETTINGS_CHANGED_SUBJECT, body=email_body, to=user.id)


def delete_from_friendship(first: User, second: User) -> None:
    request = FriendRequest.find_friend_request(first_user=first, second_user=second)

    if request:
        request.delete()
        User.delete_friends(first, second)
