from django.contrib import admin
from django.conf import settings
from plans.models import Plan, Price
import stripe


class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'allowed_users', 'allowed_domains', 'allowed_urls', 'company')
    list_display_links = ('id', 'title')
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        if not change:
            metadata = {'company_id': obj.company.id} if obj.company else {}
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_product = stripe.Product.create(name=obj.title, metadata=metadata)
            obj.stripe_product_id = stripe_product.id
        return super().save_model(request, obj, form, change)


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'frequency', 'amount')
    list_display_links = ('id', 'plan')
    list_filter = ('frequency',)
    search_fields = ('plan', 'amount')

    def save_model(self, request, obj, form, change):
        if not change:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_price = stripe.Price.create(
                unit_amount=obj.amount * 100,
                currency='eur',
                product=obj.plan.stripe_product_id,
                recurring={'interval': 'year' if obj.frequency == Price.Frequency.YEARLY else 'month'}
            )
            obj.stripe_price_id = stripe_price.id
        return super().save_model(request, obj, form, change)


admin.site.register(Plan, PlanAdmin)
admin.site.register(Price, PriceAdmin)
