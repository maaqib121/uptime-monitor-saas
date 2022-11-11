from django.urls import path
from payment_methods.api.v1.views import PaymentMethodView


urlpatterns = [
    path('', PaymentMethodView.as_view())
]
