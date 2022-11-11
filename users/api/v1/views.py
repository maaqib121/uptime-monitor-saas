from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Value
from django.db.models.functions import Concat
from users.models import User
from users.api.v1.serializers import (
    SignupSerializer,
    AuthenticateSerializer,
    UserConfirmationSerializer,
    UserSerializer,
    ProfileSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    UserSendPasswordSerializer
)
from users.permissions import (
    IsUserExists,
    IsCurrentUserAdmin,
    IsUserNotAdmin,
    IsUserPasswordNotSet,
    IsUserLessThanAllowed
)
from users.utils.common import (
    send_confirmation_email,
    send_reset_password_email,
    send_set_password_email
)

from rest_framework_simplejwt.tokens import RefreshToken
from pingApi.utils.pagination import CustomPagination


class SignupView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_confirmation_token()
            send_confirmation_email(user, serializer.get_redirect_uri())
            serializer = UserSerializer(user, context={'request': request})
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
            serializer = UserSerializer(user, context={'request': request})
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
            serializer = UserSerializer(user, context={'request': request})
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
                'user': UserSerializer(user, context={'request': request}).data
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

    def patch(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.save()
            serializer = UserSerializer(profile.user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView, CustomPagination):
    http_method_names = ('get', 'post')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (IsAuthenticated, IsCurrentUserAdmin, IsUserLessThanAllowed)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user_qs = self.request.user.company_members()
        if self.request.GET.get('search'):
            user_qs = user_qs.annotate(name=Concat('profile__first_name', Value(' '), 'profile__gitlast_name')).filter(
                name__icontains=self.request.GET['search']
            )
        return user_qs

    def get_paginated_response(self):
        page = self.paginate_queryset(self.get_queryset(), self.request)
        serializer = UserSerializer(page, many=True, context={'request': self.request})
        return super().get_paginated_response(serializer.data)

    def get(self, request):
        if 'no_paginate' in request.GET:
            serializer = UserSerializer(self.get_queryset(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return self.get_paginated_response()

    def post(self, request):
        serializer = UserSerializer(data=request.data, context={'company': request.user.company})
        if serializer.is_valid():
            user = serializer.save()
            user.generate_confirmation_token()
            send_set_password_email(user, serializer.validated_data['redirect_uri'])
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    http_method_names = ('get', 'patch', 'delete')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated, IsUserExists)
        elif self.request.method == 'PATCH':
            permission_classes = (IsAuthenticated, IsCurrentUserAdmin, IsUserExists)
        else:
            permission_classes = (IsAuthenticated, IsCurrentUserAdmin, IsUserExists, IsUserNotAdmin)
        return [permission() for permission in permission_classes]

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            serializer = UserSerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = User.objects.get(id=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSendPasswordView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated, IsCurrentUserAdmin, IsUserExists, IsUserPasswordNotSet)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, pk):
        serializer = UserSendPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(id=pk)
            user.generate_confirmation_token()
            response = send_set_password_email(user, serializer.validated_data['redirect_uri'])
            if isinstance(response, Response):
                return response
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
