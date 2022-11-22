from django.urls import path
from urls.api.v1.views import UrlView


urlpatterns = [
    path('', UrlView.as_view()),
]
