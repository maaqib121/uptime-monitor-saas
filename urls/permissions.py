from rest_framework import permissions


class IsUrlActive(permissions.BasePermission):
    message = 'URL does not exists or is inactive.'

    def has_permission(self, request, view):
        return request.user.company.url_set.filter(
            id=view.kwargs['url_id'],
            domain_id=view.kwargs['domain_id'],
            is_active=True
        ).exists()


class IsUrlLessThanAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        self.message = (
            f'Only {request.user.company.allowed_urls} urls can be added in your company in current subscribed plan. '
            'Upgrade your plan to add more urls.'
        )
        return request.user.company.url_set.count() < request.user.company.allowed_urls
