from django.urls import path, include


urlpatterns = [
    path('api/', include('domains.api.urls')),
]
