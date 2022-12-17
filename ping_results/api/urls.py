from django.urls import path, include


urlpatterns = [
    path('v1/', include('ping_results.api.v1.urls'))
]
