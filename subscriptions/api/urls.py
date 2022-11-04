from django.urls import path, include


urlpatterns = [
    path('v1/subscriptions/', include('subscriptions.api.v1.urls'))
]
