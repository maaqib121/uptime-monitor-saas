from django.urls import path, include


urlpatterns = [
    path('api/', include('ping_results.api.urls'))
]
