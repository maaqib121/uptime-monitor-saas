from django.urls import path
from users.api.v1.views import SignupView, AuthenticateView


urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('authenticate/', AuthenticateView.as_view())
]
