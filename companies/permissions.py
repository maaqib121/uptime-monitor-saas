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
