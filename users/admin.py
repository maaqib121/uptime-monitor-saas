from django.contrib import admin
from users.models import User, Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'date_joined')
    list_display_links = ('id', 'email')
    list_filter = ('is_active',)
    search_fields = ('email',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'company')
    list_display_links = ('id', 'full_name')
    list_filter = ('company__name',)
    search_fields = ('first_name', 'last_name', 'email')

    def email(self, obj):
        return obj.user.email

    def full_name(self, obj):
        return obj.full_name


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
