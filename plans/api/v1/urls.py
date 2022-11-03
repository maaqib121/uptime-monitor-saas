from django.urls import path
from plans.api.v1.views import PlanView


urlpatterns = [
    path('', PlanView.as_view())
]
