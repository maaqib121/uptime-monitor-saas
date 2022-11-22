from django.urls import path, include


urlpatterns = [
    path('v1/countries/', include('countries.api.v1.urls'))
]
