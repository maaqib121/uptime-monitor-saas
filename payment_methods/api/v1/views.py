from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from payment_methods.api.v1.serializers import PaymentMethodSerializer
from users.permissions import IsCurrentUserAdmin
from pingApi.utils.pagination import CustomPagination
import stripe


class PaymentMethodView(APIView, CustomPagination):
    http_method_names = ('get', 'post')
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin)
    authentication_classes = (JWTAuthentication,)

    def get_stripe_payment_methods(self):
        if self.request.user.company.stripe_customer_id:
            return stripe.Customer.list_payment_methods(
                self.request.user.company.stripe_customer_id,
                type='card',
                expand=['data.customer']
            )['data']
        return []

    def get_paginated_response(self):
        page = self.paginate_queryset(self.get_stripe_payment_methods(), self.request)
        serializer = PaymentMethodSerializer(page, many=True, context={'request': self.request})
        return super().get_paginated_response(serializer.data)

    def get(self, request):
        if 'no_paginate' in self.request.GET:
            serializer = PaymentMethodSerializer(self.get_stripe_payment_methods(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return self.get_paginated_response()

    def post(self, request):
        serializer = PaymentMethodSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            response_data = {'success': True}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PaymentMethodDetailView(APIView):
    http_method_names = ('patch', 'delete')
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin)
    authentication_classes = (JWTAuthentication,)

    def patch(self, request, payment_method_id):
        if request.user.company.stripe_customer_id:
            try:
                stripe.Customer.modify(
                    request.user.company.stripe_customer_id,
                    invoice_settings={'default_payment_method': payment_method_id}
                )
            except Exception as exception:
                return Response({'errors': str(exception)}, status=status.HTTP_400_BAD_REQUEST)
        response_data = {'success': True}
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, payment_method_id):
        try:
            stripe.PaymentMethod.detach(payment_method_id)
        except Exception as exception:
            return Response({'errors': str(exception)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
