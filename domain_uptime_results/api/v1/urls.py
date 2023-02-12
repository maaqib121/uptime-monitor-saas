from django.urls import path
from domain_uptime_results.api.v1.views import DomainUptimeHistoryView


urlpatterns = [
    path('domain_uptime_history/', DomainUptimeHistoryView.as_view())
]
