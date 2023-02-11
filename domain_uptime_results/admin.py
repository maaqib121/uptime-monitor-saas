from django.contrib import admin
from domain_uptime_results.models import DomainUptimeResult


class DomainUptimeResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'status', 'ssl_validity', 'status_code', 'response_time', 'created_at')
    list_display_links = ('id', 'domain')
    list_filter = ('domain', 'company')
    search_fields = ('status_code',)

    def domain(self, instance):
        return instance.domain


admin.site.register(DomainUptimeResult, DomainUptimeResultAdmin)
