from django.contrib import admin
from django.conf import settings
from plans.models import Plan, Price
import stripe


class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'allowed_urls', 'get_ping_interval', 'company')
    list_display_links = ('id', 'title')
    search_fields = ('title',)

    def get_ping_interval(self, instance):
        return instance.ping_interval

    get_ping_interval.short_description = 'Ping Interval (mins)'

    def save_model(self, request, instance, form, change):
        if not change:
            metadata = {'company_id': instance.company.id} if instance.company else {}
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_product = stripe.Product.create(name=instance.title, metadata=metadata)
            instance.stripe_product_id = stripe_product.id
        return super().save_model(request, instance, form, change)


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'frequency', 'amount')
    list_display_links = ('id', 'plan')
    list_filter = ('frequency',)
    search_fields = ('plan', 'amount')

    def save_model(self, request, instance, form, change):
        if not change:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_price = stripe.Price.create(
                unit_amount=instance.amount * 100,
                currency='eur',
                product=instance.plan.stripe_product_id,
                recurring={'interval': 'year' if instance.frequency == Price.Frequency.YEARLY else 'month'}
            )
            instance.stripe_price_id = stripe_price.id
        return super().save_model(request, instance, form, change)


admin.site.register(Plan, PlanAdmin)
admin.site.register(Price, PriceAdmin)
