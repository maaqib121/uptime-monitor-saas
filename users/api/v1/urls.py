from django.urls import path
from users.api.v1.views import SignupView, AuthenticateView, UserConfirmationView


urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('authenticate/', AuthenticateView.as_view()),
    path('users/confirm/<uidb64>/<token>/', UserConfirmationView.as_view())
]
