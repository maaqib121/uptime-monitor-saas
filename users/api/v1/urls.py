from django.urls import path
from users.api.v1.views import (
    SignupView,
    AuthenticateView,
    UserConfirmationView,
    VerifyConfirmationTokenView,
    ForgetPasswordView,
    ResetPasswordView,
    UserProfileView,
    UserView,
    UserDetailView,
    UserSendPasswordView,
    RequestPhoneOtpView,
    UserPhoneVerifyView
)


urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('authenticate/', AuthenticateView.as_view()),
    path('users/confirm/<uidb64>/<token>/', UserConfirmationView.as_view()),
    path('verify_confirmation_token/<uidb64>/<token>/', VerifyConfirmationTokenView.as_view()),
    path('forget_password/', ForgetPasswordView.as_view()),
    path('reset_password/<uidb64>/<token>/', ResetPasswordView.as_view()),
    path('users/profile/', UserProfileView.as_view()),
    path('users/', UserView.as_view()),
    path('users/<int:pk>/', UserDetailView.as_view()),
    path('users/<int:pk>/send_password/', UserSendPasswordView.as_view()),
    path('users/request_phone_otp/', RequestPhoneOtpView.as_view()),
    path('users/verify_phone/', UserPhoneVerifyView.as_view())
]
