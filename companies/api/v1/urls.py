from django.urls import path
from companies.api.v1.views import CompanyView, CompanyQuotationView


urlpatterns = [
    path('', CompanyView.as_view()),
    path('quotation/', CompanyQuotationView.as_view())
]
