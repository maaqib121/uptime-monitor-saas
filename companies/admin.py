from django.contrib import admin
from django import forms
from companies.models import Company
from users.models import User


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.filter(profile__company=self.instance)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    form = CompanyForm


admin.site.register(Company, CompanyAdmin)
