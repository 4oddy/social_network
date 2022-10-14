from rest_framework.permissions import BasePermission


class InDialog(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.second_user == request.user


class InConservation(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all()
