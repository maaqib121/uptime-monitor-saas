from django.urls import path
from countries.api.v1.views import CountryView


urlpatterns = [
    path('', CountryView.as_view()),
]
