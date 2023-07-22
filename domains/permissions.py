from rest_framework import permissions


class IsDomainExists(permissions.BasePermission):
    message = 'Domain does not exists.'

    def has_permission(self, request, view):
        view.domain = request.user.company.domain_set.filter(id=view.kwargs['domain_id']).first()
        return True if view.domain else False
