from django.urls import path
from domains.api.v1.views import DomainView


urlpatterns = [
    path('', DomainView.as_view()),
]
