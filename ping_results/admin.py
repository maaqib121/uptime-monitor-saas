from django.contrib import admin
from ping_results.models import PingResult


class PingResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'domain', 'status_code', 'company', 'created_at')
    list_display_links = ('url', 'domain', 'company')
    list_filter = ('url', 'company')
    search_fields = ('status_code',)

    def domain(self, instance):
        return instance.domain


admin.site.register(PingResult, PingResultAdmin)
