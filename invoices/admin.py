from django.contrib import admin
from invoices.models import Invoice


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'plan_name', 'amount_paid', 'paid', 'created_at')
    list_display_links = ('id', 'company')
    list_filter = ('company', 'paid')
    search_fields = ('plan', 'company')


admin.site.register(Invoice, InvoiceAdmin)
