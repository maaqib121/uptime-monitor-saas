from django.urls import path
from domains.api.v1.views import DomainView, DomainDetailView


urlpatterns = [
    path('', DomainView.as_view()),
    path('<int:pk>/', DomainDetailView.as_view()),
]
