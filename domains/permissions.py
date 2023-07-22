from rest_framework import permissions


class IsDomainExists(permissions.BasePermission):
    message = 'Domain does not exists.'

    def has_permission(self, request, view):
        view.domain = request.user.company.domain_set.filter(id=view.kwargs['domain_id']).first()
        return True if view.domain else False


class IsDomainLessThanAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        self.message = (
            f'Only {request.user.company.allowed_domains} domains can be added in your company in current subscribed plan. '
            'Upgrade your plan to add more domains.'
        )
        return request.user.company.domain_set.count() < request.user.company.allowed_domains
