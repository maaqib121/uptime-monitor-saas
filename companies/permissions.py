from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import status


class GenericAPIException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'error'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class IsTrialActiveOrSubscribed(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.company.remaining_trail_days <= 0 and not request.user.company.is_subscription_active:
            raise GenericAPIException('Trial expired. Please subscribe to a plan', status_code=status.HTTP_402_PAYMENT_REQUIRED)
        return True
