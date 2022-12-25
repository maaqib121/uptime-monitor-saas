from django.urls import path, include
from urls.api.v1.views import UrlView, UrlDetailView, UrlRequestFileView, UrlExportView

app_name = 'urls'


urlpatterns = [
    path('', UrlView.as_view()),
    path('<int:url_id>/', UrlDetailView.as_view()),
    path('request_file/', UrlRequestFileView.as_view()),
    path('export/', UrlExportView.as_view(), name='export'),
    path('<int:url_id>/', include('ping_results.api.v1.urls')),
]
