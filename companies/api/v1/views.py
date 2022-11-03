from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from companies.api.v1.serializers import CompanySerializer


class CompanyView(APIView):
    http_method_names = ('get', 'patch')
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        serializer = CompanySerializer(request.user.company, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = CompanySerializer(request.user.company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer = CompanySerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
