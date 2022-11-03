from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from users.api.v1.serializers import (
    SignupSerializer,
    AuthenticateSerializer,
    UserConfirmationSerializer,
    UserSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer
)
from users.utils.common import send_confirmation_email, send_reset_password_email
from rest_framework_simplejwt.tokens import RefreshToken


class SignupView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_confirmation_token()
            send_confirmation_email(user, serializer.get_redirect_uri())
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserConfirmationView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        request_data = request.data.copy()
        request_data.update({'uidb64': uidb64, 'token': token})
        serializer = UserConfirmationSerializer(data=request_data)
        if serializer.is_valid():
            user = serializer.get_user()
            user.clear_confirmation_token()
            user.activate()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyConfirmationTokenView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        request_data = request.data.copy()
        request_data.update({'uidb64': uidb64, 'token': token})
        serializer = UserConfirmationSerializer(data=request_data)
        if serializer.is_valid():
            user = serializer.get_user()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AuthenticateView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = AuthenticateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.get_user()
            refresh = RefreshToken.for_user(user)
            response_data = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserSerializer(user).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.get_user()
            user.generate_confirmation_token()
            response = send_reset_password_email(user, serializer.validated_data['redirect_uri'])
            if isinstance(response, Response):
                return response
            response_data = {'success': True}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        form_data = request.data.copy()
        form_data.update({'uidb64': uidb64, 'token': token})
        serializer = ResetPasswordSerializer(data=form_data)
        if serializer.is_valid():
            user = serializer.get_user()
            user.update_password(serializer.validated_data['password'])
            user.clear_confirmation_token()
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    http_method_names = ('get', 'patch')
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
