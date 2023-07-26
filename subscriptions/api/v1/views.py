from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from subscriptions.api.v1.serializers import SubscriptionSerializer
from plans.api.v1.serializers import PriceSerializer
from subscriptions.utils.stripe import (
    get_or_create_stripe_customer,
    create_stripe_subscription,
    update_stripe_subscription,
    delete_stripe_subscription
)
from users.permissions import IsCurrentUserAdmin
from domains.permissions import IsDomainActive, IsSubscribed


class SubscriptionView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin, IsDomainActive)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, domain_id):
        request_data = request.data.copy()
        request_data.update({'domain': domain_id, 'company': request.user.company_id})
        serializer = SubscriptionSerializer(data=request_data)
        if serializer.is_valid():
            stripe_customer = get_or_create_stripe_customer(request.user)

            if self.domain.stripe_subscription_id:
                stripe_subscription, is_created = update_stripe_subscription(
                    stripe_customer,
                    serializer.validated_data['plan_price'],
                    self.domain,
                    request.user
                )
            else:
                stripe_subscription, is_created = create_stripe_subscription(
                    stripe_customer,
                    serializer.validated_data['plan_price'],
                    self.domain,
                    request.user
                )

            if is_created:
                response_data = {
                    'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret,
                    'price': PriceSerializer(serializer.validated_data['plan_price']).data
                }
            else:
                response_data = {'success': True}

            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionCancelView(APIView):
    http_method_names = ('delete',)
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin, IsDomainActive, IsSubscribed)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request):
        delete_stripe_subscription(self.domain)
        self.domain.clear_subscription()
        return Response(status=status.HTTP_204_NO_CONTENT)
