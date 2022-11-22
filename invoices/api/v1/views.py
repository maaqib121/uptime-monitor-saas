from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from invoices.api.v1.serializers import InvoiceSerializer
from users.permissions import IsCurrentUserAdmin


class InvoiceView(APIView):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication, IsCurrentUserAdmin)

    def get_queryset(self):
        return self.request.user.company.invoice_set.filter(paid=True)

    def get(self, request):
        serializer = InvoiceSerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
