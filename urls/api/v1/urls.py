from django.urls import path, include
from urls.api.v1.views import UrlView, UrlDetailView, UrlExportView


urlpatterns = [
    path('', UrlView.as_view()),
    path('<int:url_id>/', UrlDetailView.as_view()),
    path('export/', UrlExportView.as_view()),
    path('<int:url_id>/', include('ping_results.api.v1.urls')),
]
