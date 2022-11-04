from django.urls import path
from webhooks.views import StripeWebhookView


urlpatterns = [
    path('stripe/', StripeWebhookView.as_view())
]
