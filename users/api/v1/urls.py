from django.urls import path
from users.api.v1.views import SignupView


urlpatterns = [
    path('signup/', SignupView.as_view())
]
