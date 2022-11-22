from django.urls import path, include


urlpatterns = [
    path('v1/invoices/', include('invoices.api.v1.urls'))
]
