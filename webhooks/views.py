from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from plans.models import Price
from invoices.models import Invoice
from datetime import datetime
import stripe


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
            price = Price.objects.filter(stripe_price_id=event.data.object.lines.data[0].plan.id).first()
            Invoice.objects.create(
                stripe_invoice_id=event.data.object.id,
                amount=event.data.object.lines.data[0].amount,
                plan_name=f'{price.plan} - {price.get_frequency_display()}',
                company_id=event.data.object.lines.data[0].metadata['company_id'],
                created_at=datetime.fromtimestamp(event.data.object.created)
            )

        elif event.type == 'invoice.payment_succeeded':
            Invoice.objects.filter(stripe_invoice_id=event.data.object.id).update(paid=True)

        elif event.type == 'payment_intent.succeeded':
            print('Payment intent succeeded')

        response_data = {'success': True}
        return Response(response_data, status=status.HTTP_200_OK)
