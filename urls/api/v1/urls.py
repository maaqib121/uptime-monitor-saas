from django.urls import path
from urls.api.v1.views import UrlView, UrlDetailView


urlpatterns = [
    path('', UrlView.as_view()),
    path('<int:url_id>/', UrlDetailView.as_view())
]
