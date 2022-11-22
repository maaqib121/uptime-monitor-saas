from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from companies.models import Company
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
            stripe_subscription = stripe.Subscription.retrieve(event.data.object.subscription)
            price = Price.objects.filter(stripe_price_id=event.data.object.lines.data[0].plan.id).first()
            Invoice.objects.create(
                stripe_invoice_id=event.data.object.id,
                invoice_url=event.data.object.invoice_pdf,
                amount=event.data.object.subtotal / 100,
                plan_name=f'{price.plan} - {price.get_frequency_display()}',
                company_id=stripe_subscription.metadata['company_id'],
                created_at=datetime.fromtimestamp(event.data.object.created)
            )

        elif event.type == 'invoice.payment_succeeded':
            stripe_subscription = stripe.Subscription.retrieve(event.data.object.subscription)
            Invoice.objects.filter(stripe_invoice_id=event.data.object.id).update(paid=True)
            company = Company.objects.filter(id=stripe_subscription.metadata['company_id']).first()
            price = Price.objects.filter(stripe_price_id=event.data.object.lines.data[-1].price.id).first()
            if company and price:
                company.subscribed_plan = price
                company.is_subscription_active = True
                company.save()

        elif event.type == 'payment_intent.succeeded':
            if event.data.object['payment_method']:
                stripe.PaymentMethod.attach(event.data.object.payment_method, customer=event.data.object.customer,)
                stripe.Customer.modify(
                    event.data.object.customer,
                    invoice_settings={'default_payment_method': event.data.object.payment_method}
                )

        response_data = {'success': True}
        return Response(response_data, status=status.HTTP_200_OK)
