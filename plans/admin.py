from django.contrib import admin
from plans.models import Plan, Price


class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'allowed_users', 'allowed_domains', 'allowed_urls')
    list_display_links = ('id', 'title')
    search_fields = ('title',)


class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'frequency', 'amount')
    list_display_links = ('id', 'plan')
    list_filter = ('frequency',)
    search_fields = ('plan', 'amount')


admin.site.register(Plan, PlanAdmin)
admin.site.register(Price, PriceAdmin)
