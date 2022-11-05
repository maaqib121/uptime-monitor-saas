from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.conf import settings
from subscriptions.api.v1.serializers import SubscriptionSerializer
from plans.api.v1.serializers import PriceSerializer
import stripe


class SubscriptionView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data, context={'company': request.user.company})
        if serializer.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY
            if not request.user.company.stripe_customer_id:
                stripe_customer = stripe.Customer.create(
                    name=request.user.company.name,
                    email=request.user.email,
                    metadata={'company_id': request.user.company.id, 'user_id': request.user.id}
                )
                request.user.company.set_stripe_customer_id(stripe_customer.id)

            if request.user.company.stripe_subscription_id:
                subscription = stripe.Subscription.retrieve(request.user.company.stripe_subscription_id)
                stripe_subscription = stripe.Subscription.modify(
                    subscription.id,
                    cancel_at_period_end=False,
                    proration_behavior='always_invoice',
                    items=[{
                        'id': subscription['items']['data'][0].id,
                        'price': serializer.validated_data['plan_price'].stripe_price_id
                    }],
                    metadata={'company_id': request.user.company.id, 'user_id': request.user.id}
                )
                response_data = {'success': True}
            else:
                stripe_subscription = stripe.Subscription.create(
                    customer=request.user.company.stripe_customer_id,
                    off_session=True,
                    payment_behavior='default_incomplete',
                    items=[{'price': serializer.validated_data['plan_price'].stripe_price_id}],
                    expand=['latest_invoice.payment_intent'],
                    metadata={'company_id': request.user.company.id, 'user_id': request.user.id}
                )
                request.user.company.set_stripe_subscription_id(stripe_subscription.id)
                response_data = {
                    'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret,
                    'price': PriceSerializer(serializer.validated_data['plan_price']).data
                }

            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
