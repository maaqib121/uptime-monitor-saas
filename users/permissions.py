from rest_framework import permissions
from users.models import User


class IsUserExists(permissions.BasePermission):
    message = 'User does not exists.'

    def has_permission(self, request, view):
        return User.objects.filter(profile__company=request.user.company, id=view.kwargs['pk']).exists()
