from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from companies.api.v1.serializers import (
    CompanySerializer,
    CompanyQuotationSerializer,
    GoogleAuthenticateSerializer,
    GoogleDissociateSerializer
)
from companies.utils.common import send_quotation_email
from users.permissions import IsCurrentUserAdmin


class CompanyView(APIView):
    http_method_names = ('get', 'patch')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (IsAuthenticated, IsCurrentUserAdmin)
        return [permission() for permission in permission_classes]

    def get(self, request):
        serializer = CompanySerializer(request.user.company, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = CompanySerializer(request.user.company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer = CompanySerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CompanyQuotationView(APIView):
    http_method_names = ('post',)

    def post(self, request):
        serializer = CompanyQuotationSerializer(data=request.data)
        if serializer.is_valid():
            response = send_quotation_email(
                request.user,
                serializer.validated_data['allowed_users'],
                serializer.validated_data['allowed_domains'],
                serializer.validated_data['allowed_urls'],
                serializer.validated_data['ping_interval'],
                serializer.validated_data['body']
            )
            if isinstance(response, Response):
                return response
            response_data = {'success': True}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthenticateView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        serializer = GoogleAuthenticateSerializer(request.user.company, data=request.data)
        if serializer.is_valid():
            serializer = CompanySerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GoogleDissociateView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        serializer = GoogleDissociateSerializer(request.user.company, data=request.data)
        if serializer.is_valid():
            serializer = CompanySerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
