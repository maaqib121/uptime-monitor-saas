from rest_framework import serializers
from rest_framework.fields import empty
from django.conf import settings
import stripe


class PaymentMethodSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

    def validate(self, attrs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not self.context['user'].company.stripe_customer_id:
            stripe_customer = stripe.Customer.create(
                name=self.context['user'].company.name,
                email=self.context['user'].email,
                metadata={'company_id': self.context['user'].company.id, 'user_id': self.context['user'].id}
            )
            self.context['user'].company.set_stripe_customer_id(stripe_customer.id)

        try:
            stripe.PaymentMethod.attach(attrs['payment_method_id'], customer=self.context['user'].company.stripe_customer_id)
        except Exception as exception:
            raise serializers.ValidationError(str(exception))
        return super().validate(attrs)
