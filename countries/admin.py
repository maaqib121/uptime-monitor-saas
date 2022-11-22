from django.contrib import admin
from countries.models import Country


class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'continent', 'is_active')
    list_filter = ('continent', 'is_active')
    list_display_links = ('id', 'name')
    ordering = ('id',)
    search_fields = ('name', 'code')

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Country, CountryAdmin)
