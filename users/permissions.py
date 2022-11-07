from rest_framework import permissions
from users.models import User


class IsUserExists(permissions.BasePermission):
    message = 'User does not exists.'

    def has_permission(self, request, view):
        return User.objects.filter(profile__company=request.user.company, id=view.kwargs['pk']).exists()


class IsCurrentUserAdmin(permissions.BasePermission):
    message = 'Only company admin has the permission to perform this action.'

    def has_permission(self, request, view):
        return request.user.is_company_admin


class IsUserNotAdmin(permissions.BasePermission):
    message = 'You do not have permission to delete company admin.'

    def has_permission(self, request, view):
        return User.objects.filter(
            profile__company=request.user.company,
            profile__is_company_admin=False,
            id=view.kwargs['pk']
        ).exists()


class IsUserPasswordNotSet(permissions.BasePermission):
    message = 'Password already set by user.'

    def has_permission(self, request, view):
        user = User.objects.filter(profile__company=request.user.company, id=view.kwargs['pk']).first()
        return not (user.password and user.has_usable_password)
