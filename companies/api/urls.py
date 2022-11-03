from django.urls import path, include


urlpatterns = [
    path('v1/company/', include('companies.api.v1.urls'))
]
