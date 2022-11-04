from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
import stripe
import json


class StripeWebhookView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = None
        payload = request.body
        sig_header = request.headers['STRIPE_SIGNATURE']
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SIGNING_SECRET)
        except ValueError as exception:
            response_data = {'error': str(exception)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as exception:
            response_data = {'error': str(exception)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if event.type == 'invoice.created':
            print('Invoice created')
            print(json.dumps(event))

        elif event.type == 'invoice.payment_succeeded':
            print('Invoice payment succeeded')
            print(json.dumps(event))

        elif event.type == 'payment_intent.succeeded':
            print('Payment intent succeeded')
            print(json.dumps(event))

        response_data = {'success': True}
        return Response(response_data, status=status.HTTP_200_OK)
