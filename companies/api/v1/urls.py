from django.urls import path
from companies.api.v1.views import CompanyView


urlpatterns = [
    path('', CompanyView.as_view())
]
