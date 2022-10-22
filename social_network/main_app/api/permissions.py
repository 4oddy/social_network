from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanAcceptOrDenyFriendRequest(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.to_user == request.user


class CanEditOrDeletePost(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
