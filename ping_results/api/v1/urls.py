from django.urls import path
from ping_results.api.v1.views import PingHistoryView, HealthRateView


urlpatterns = [
    path('ping_history/', PingHistoryView.as_view()),
    path('health_rate/', HealthRateView.as_view())
]
