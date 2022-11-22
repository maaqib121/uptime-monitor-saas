from rest_framework import serializers
from invoices.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = ('stripe_invoice_id', 'company')
