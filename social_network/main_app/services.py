from django.db.models import Q, functions
from django.contrib.auth import get_user_model

from .models import FriendRequest

User = get_user_model()


def find_users(username):
    queryset = User.objects.annotate(lower_username=functions.Lower('username'))
    queryset = queryset.filter(Q(lower_username=username) | Q(lower_username__startswith=username) |
                               Q(lower_username__endswith=username))
    return queryset


def find_friend_request(first_user, second_user):
    queryset = FriendRequest.objects.filter(Q(from_user=first_user) & Q(to_user=second_user) |
                                            Q(from_user=second_user) | Q(to_user=first_user)).first()
    return queryset
