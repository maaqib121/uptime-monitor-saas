from django.urls import path
from payment_methods.api.v1.views import PaymentMethodView, PaymentMethodDetailView


urlpatterns = [
    path('', PaymentMethodView.as_view()),
    path('<str:payment_method_id>/', PaymentMethodDetailView.as_view())
]
