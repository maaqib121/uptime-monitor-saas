from rest_framework import permissions


class IsDomainActive(permissions.BasePermission):
    message = 'Domain does not exists or is inactive.'

    def has_permission(self, request, view):
        view.domain = request.user.company.domain_set.filter(id=view.kwargs['domain_id'], is_active=True).first()
        return True if view.domain else False


class IsSubscribed(permissions.BasePermission):
    def has_permission(self, request, view):
        return view.domain.is_subscription_active
