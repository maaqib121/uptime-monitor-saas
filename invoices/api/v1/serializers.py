from rest_framework import serializers
from rest_framework.fields import empty
from invoices.models import Invoice
from domains.api.v1.serializers import DomainSerializer


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = ('stripe_invoice_id', 'company')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['domain'] = DomainSerializer(context={
            'no_labels': True,
            'no_users': True,
            'no_total_urls': True,
            'no_last_health_score': True,
            'no_last_uptime_result': True
        })
