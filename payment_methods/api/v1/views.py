from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from payment_methods.api.v1.serializers import PaymentMethodSerializer
from users.permissions import IsCurrentUserAdmin
import stripe


class PaymentMethodView(APIView):
    http_method_names = ('get', 'post')
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if request.user.company.stripe_customer_id:
            stripe_payment_methods = stripe.Customer.list_payment_methods(
                request.user.company.stripe_customer_id,
                type='card'
            )['data']
        else:
            stripe_payment_methods = []
        return Response(stripe_payment_methods, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PaymentMethodSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            response_data = {'success': True}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
