from rest_framework import permissions


class IsDomainLessThanAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        self.message = (
            f'Only {request.user.company.allowed_domains} domains can be added in your company in current subscribed plan. '
            'Upgrade your plan to add more domains.'
        )
        return request.user.company.domain_set.count() < request.user.company.allowed_domains
