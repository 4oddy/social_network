from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import FriendRequest
from core.utils import get_current_date
from .tasks import send_email

User = get_user_model()


def in_friendship(first: User, second: User) -> bool:
    return first in second.friends.all() and second in first.friends.all()


def find_users(username: str) -> QuerySet:
    queryset = User.objects.filter(username__icontains=username)
    return queryset


def find_friend_request(first_user: User | None = None, second_user: User | None = None,
                        first_user_id: int | None = None, second_user_id: int | None = None) -> FriendRequest:
    request = None

    if first_user and second_user:
        request = FriendRequest.objects.filter(Q(from_user=first_user) & Q(to_user=second_user) |
                                               Q(from_user=second_user) & Q(to_user=first_user)).first()
    elif first_user and second_user_id:
        request = FriendRequest.objects.filter(Q(from_user=first_user) & Q(to_user_id=second_user_id) |
                                               Q(from_user_id=second_user_id) & Q(to_user=first_user)).first()
    elif first_user_id and second_user:
        request = FriendRequest.objects.filter(Q(from_user_id=first_user_id) & Q(to_user=second_user) |
                                               Q(from_user=second_user) & Q(to_user_id=first_user_id)).first()
    elif first_user_id and second_user_id:
        request = FriendRequest.objects.filter(Q(from_user_id=first_user_id) & Q(to_user_id=second_user_id) |
                                               Q(from_user_id=second_user_id) & Q(to_user_id=first_user_id)).first()

    return request


# func to get data from hidden form's fields
def get_data_for_action(request: HttpRequest) -> dict:
    user_path = request.POST['current_path']
    from_user_id = request.user.pk
    from_user = request.user
    to_user_id = request.POST['user_id']

    return {'user_path': user_path, 'from_user_id': from_user_id, 'from_user': from_user,
            'to_user_id': to_user_id}


def get_username_from_kwargs(kwargs: dict) -> str:
    return kwargs['username'].replace('@', '')


def create_friend_request(from_user: User | None = None, from_user_id: User | None = None,
                          to_user: User | None = None, to_user_id: User | None = None) -> FriendRequest:
    request = None

    if from_user and to_user:
        if find_friend_request(first_user=from_user, second_user=to_user) is None:
            request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)

    elif from_user and to_user_id:
        if find_friend_request(first_user=from_user, second_user_id=to_user_id) is None:
            request = FriendRequest.objects.create(from_user=from_user, to_user_id=to_user_id)

    elif from_user_id and to_user:
        if find_friend_request(first_user_id=from_user_id, second_user=to_user) is None:
            request = FriendRequest.objects.create(from_user_id=from_user_id, to_user=to_user)

    elif from_user_id and to_user_id:
        if find_friend_request(first_user_id=from_user_id, second_user_id=to_user_id) is None:
            request = FriendRequest.objects.create(from_user_id=from_user_id, to_user_id=to_user_id)

    if settings.SEND_EMAILS:
        if not to_user:
            to_user = get_object_or_404(User, pk=to_user_id)

        name = to_user.first_name if to_user.first_name else to_user.username

        if not from_user:
            from_user = get_object_or_404(User, pk=from_user_id)

        username = from_user.username

        email_body = settings.DEFAULT_EMAIL_FRIEND_REQUEST_BODY.format(name=name, name_requested=username,
                                                                       date=get_current_date())

        send_email.delay(subject=settings.DEFAULT_EMAIL_FRIEND_REQUEST_SUBJECT, body=email_body, to=[to_user.email])

    return request


def send_email_login(user: User) -> None:
    if settings.SEND_EMAILS:
        name = user.first_name if user.first_name else user.username
        username = user.username

        email_body = settings.DEFAULT_EMAIL_LOGIN_BODY.format(name=name, username=username, date=get_current_date())

        send_email.delay(subject=settings.DEFAULT_EMAIL_LOGIN_SUBJECT, body=email_body, to=[user.email])


def send_email_changed_settings(user: User) -> None:
    if settings.SEND_EMAILS:
        name = user.first_name if user.first_name else user.username

        email_body = settings.DEFAULT_EMAIL_SETTINGS_CHANGED_BODY.format(name=name, date=get_current_date())

        send_email.delay(subject=settings.DEFAULT_EMAIL_SETTINGS_CHANGED_SUBJECT, body=email_body, to=[user.email])


def delete_from_friendship(first: User, second: User) -> None:
    request = find_friend_request(first_user=first, second_user=second)

    if request:
        request.delete()
        User.delete_friends(first, second)
