from django.urls import path
from subscriptions.api.v1.views import SubscriptionView


urlpatterns = [
    path('', SubscriptionView.as_view())
]
