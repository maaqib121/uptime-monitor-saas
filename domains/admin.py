from django.contrib import admin
from django import forms
from domains.models import Domain, DomainLabel
from django.forms import Textarea


class DomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alert_emails'].widget = Textarea()
        self.fields['alert_emails'].delimiter = '\n'


class DomainAdmin(admin.ModelAdmin):
    form = DomainForm
    list_display = ('id', 'domain_url', 'is_active', 'country', 'company', 'labels')
    list_display_links = ('id', 'domain_url')
    list_filter = ('is_active', 'company')
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
