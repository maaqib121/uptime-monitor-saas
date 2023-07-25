from django.urls import path
from subscriptions.api.v1.views import SubscriptionView, SubscriptionCancelView


urlpatterns = [
    path('', SubscriptionView.as_view()),
    path('cancel/', SubscriptionCancelView.as_view())
]
