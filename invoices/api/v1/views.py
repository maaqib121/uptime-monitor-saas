from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from invoices.api.v1.serializers import InvoiceSerializer
from users.permissions import IsCurrentUserAdmin
from pingApi.utils.pagination import CustomPagination


class InvoiceView(APIView, CustomPagination):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication, IsCurrentUserAdmin)

    def get_queryset(self):
        return self.request.user.company.invoice_set.filter(paid=True)

    def get_paginated_response(self):
        page = self.paginate_queryset(self.get_queryset(), self.request)
        serializer = InvoiceSerializer(page, many=True, context={'request': self.request})
        return super().get_paginated_response(serializer.data)

    def get(self, request):
        if 'no_paginate' in request.GET:
            serializer = InvoiceSerializer(self.get_queryset(), many=True, context={'request': self.request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return self.get_paginated_response()
