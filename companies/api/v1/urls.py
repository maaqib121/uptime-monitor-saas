from django.urls import path
from companies.api.v1.views import CompanyView, CompanyQuotationView, GoogleAuthenticateView, GoogleDissociateView


urlpatterns = [
    path('', CompanyView.as_view()),
    path('quotation/', CompanyQuotationView.as_view()),
    path('authenticate_google/', GoogleAuthenticateView.as_view()),
    path('dissociate_google/', GoogleDissociateView.as_view())
]
