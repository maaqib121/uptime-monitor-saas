from django.urls import path, include


urlpatterns = [
    path('v1/plans/', include('plans.api.v1.urls'))
]
