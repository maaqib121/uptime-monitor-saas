from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from users.permissions import IsCurrentUserAdmin
import stripe


class PaymentMethodView(APIView):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if request.user.company.stripe_customer_id:
            stripe_payment_methods = stripe.PaymentMethod.list(
                customer=request.user.company.stripe_customer_id,
                type='card'
            )['data']
        else:
            stripe_payment_methods = []
        return Response(stripe_payment_methods, status=status.HTTP_200_OK)
