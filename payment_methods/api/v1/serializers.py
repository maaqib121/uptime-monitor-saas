from rest_framework import serializers
from rest_framework.fields import empty
from django.conf import settings
from datetime import datetime
from pytz import timezone
import stripe


class PaymentMethodSerializer(serializers.Serializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['id'] = serializers.CharField()
            self.fields['billing_details'] = serializers.DictField()
            self.fields['card'] = serializers.DictField()
            self.fields['created_at'] = serializers.SerializerMethodField()
            self.fields['type'] = serializers.CharField()
            self.fields['is_default_payment_method'] = serializers.SerializerMethodField()
        else:
            self.fields['payment_method_id'] = serializers.CharField()

    def get_created_at(self, instance):
        return datetime.utcfromtimestamp(instance.created)

    def get_is_default_payment_method(self, instance):
        return instance.id == instance.customer.invoice_settings.default_payment_method

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
