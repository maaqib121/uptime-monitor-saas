from django.contrib import admin
from companies.models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


admin.site.register(Company, CompanyAdmin)
