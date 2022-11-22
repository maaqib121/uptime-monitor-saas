from django.urls import path, include


urlpatterns = [
    path('v1/domains/', include('domains.api.v1.urls')),
]
