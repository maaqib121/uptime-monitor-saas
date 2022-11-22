from django.contrib import admin
from urls.models import Url, UrlLabel


class UrlAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'domain')
    list_display_links = ('id', 'url')
    list_filter = ('domain',)
    search_fields = ('url',)

    def labels(self, instance):
        return list(instance.urllabel_set.values_list('label', flat=True))


class UrlLabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'url')
    list_display_links = ('id', 'label')
    list_filter = ('url',)
    search_fields = ('label',)


admin.site.register(Url, UrlAdmin)
admin.site.register(UrlLabel, UrlLabelAdmin)
