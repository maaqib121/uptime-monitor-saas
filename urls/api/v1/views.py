from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from urls.models import Url
from urls.api.v1.serializers import UrlSerializer
from companies.permissions import IsTrialActiveOrSubscribed
from domains.permissions import IsDomainExists
from users.permissions import IsCurrentUserAdmin
from urls.permissions import IsUrlExists, IsUrlLessThanAllowed
from pingApi.utils.pagination import CustomPagination


class UrlView(APIView, CustomPagination):
    http_method_names = ('get', 'post')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated, IsTrialActiveOrSubscribed, IsDomainExists)
        else:
            permission_classes = (
                IsAuthenticated,
                IsTrialActiveOrSubscribed,
                IsCurrentUserAdmin,
                IsDomainExists,
                IsUrlLessThanAllowed
            )
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        url_qs = self.request.user.company.url_set.filter(domain_id=self.kwargs['domain_id'])
        if self.request.GET.get('search'):
            url_qs = url_qs.filter(url__icontains=self.request.GET['search'])
        return url_qs

    def get_paginated_response(self):
        page = self.paginate_queryset(self.get_queryset(), self.request)
        serializer = UrlSerializer(page, many=True, context={'request': self.request})
        return super().get_paginated_response(serializer.data)

    def get(self, request, domain_id):
        if 'no_paginate' in request.GET:
            serializer = UrlSerializer(self.get_queryset(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return self.get_paginated_response()

    def post(self, request, domain_id):
        request_data = request.data.copy()
        request_data.update({'company': request.user.company.id, 'domain': domain_id})
        serializer = UrlSerializer(data=request_data)
        if serializer.is_valid():
            serializer = UrlSerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UrlDetailView(APIView):
    http_method_names = ('get', 'patch', 'delete')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated, IsTrialActiveOrSubscribed, IsUrlExists)
        elif self.request.method == 'PATCH':
            permission_classes = (IsAuthenticated, IsTrialActiveOrSubscribed, IsCurrentUserAdmin, IsUrlExists)
        else:
            permission_classes = (IsAuthenticated, IsTrialActiveOrSubscribed, IsCurrentUserAdmin, IsUrlExists)
        return [permission() for permission in permission_classes]

    def get(self, request, domain_id, url_id):
        url = Url.objects.get(id=url_id)
        serializer = UrlSerializer(url, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, domain_id, url_id):
        url = Url.objects.get(id=url_id)
        serializer = UrlSerializer(url, data=request.data, partial=True, context={'company': request.user.company})
        if serializer.is_valid():
            serializer = UrlSerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, domain_id, url_id):
        url = Url.objects.get(id=url_id)
        url.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
