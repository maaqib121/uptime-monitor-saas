from django.urls import path
from ping_results.api.v1.views import PingHistoryView


urlpatterns = [
    path('ping_history/', PingHistoryView.as_view())
]
