from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from users.api.v1.serializers import SignupSerializer, AuthenticateSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class SignupView(APIView):
    http_method_names = ('post',)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer = UserSerializer(serializer.save())
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
