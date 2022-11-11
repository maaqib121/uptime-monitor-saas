from django.urls import path, include


urlpatterns = [
    path('v1/payment_methods/', include('payment_methods.api.v1.urls'))
]
