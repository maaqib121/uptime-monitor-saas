from django.contrib import admin
from urls.models import Url, UrlLabel


class UrlAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'is_active', 'domain', 'company', 'last_ping_status_code', 'last_alert_date_time', 'labels')
    list_display_links = ('id', 'url')
    list_filter = ('is_active', 'domain', 'company')
    search_fields = ('url',)
    readonly_fields = ('last_ping_status_code', 'last_alert_date_time')

    def labels(self, instance):
        return list(instance.urllabel_set.values_list('label', flat=True))


class UrlLabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'url')
    list_display_links = ('id', 'label')
    list_filter = ('url',)
    search_fields = ('label',)


admin.site.register(Url, UrlAdmin)
admin.site.register(UrlLabel, UrlLabelAdmin)
