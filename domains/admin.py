from django.contrib import admin
from domains.models import Domain, DomainLabel


class DomainAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain_url', 'country', 'company', 'labels')
    list_display_links = ('id', 'domain_url')
    list_filter = ('company',)
    search_fields = ('domain_url',)

    def labels(self, instance):
        return list(instance.domainlabel_set.values_list('label', flat=True))


class DomainLabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'domain')
    list_display_links = ('id', 'label')
    list_filter = ('domain',)
    search_fields = ('label',)


admin.site.register(Domain, DomainAdmin)
admin.site.register(DomainLabel, DomainLabelAdmin)
