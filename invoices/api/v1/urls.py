from django.urls import path
from invoices.api.v1.views import InvoiceView


urlpatterns = [
    path('', InvoiceView.as_view())
]
