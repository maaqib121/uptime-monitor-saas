from django.urls import path, include


urlpatterns = [
    path('v1/', include('countries.api.v1.urls'))
]
