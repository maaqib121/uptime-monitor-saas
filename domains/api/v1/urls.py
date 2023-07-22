from django.urls import path, include
from domains.api.v1.views import DomainView, DomainDetailView


urlpatterns = [
    path('', DomainView.as_view()),
    path('<int:domain_id>/', DomainDetailView.as_view()),
    path('<int:domain_id>/urls/', include('urls.api.v1.urls')),
    path('<int:domain_id>/', include('ping_results.api.v1.urls')),
    path('<int:domain_id>/', include('domain_uptime_results.api.v1.urls')),
    path('<int:domain_id>/subscriptions/', include('subscriptions.api.v1.urls')),
]
