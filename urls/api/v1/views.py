from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Q
from domains.models import Domain
from urls.models import Url
from urls.api.v1.serializers import UrlSerializer, UrlCreateSerializer, UrlRequestFileSerializer, UrlExportSerializer
from urls.utils.export import export_to_csv, export_to_xls
from companies.permissions import IsTrialActiveOrSubscribed
from domains.permissions import IsDomainExists
from urls.permissions import IsUrlExists, IsUrlLessThanAllowed
from pingApi.utils.pagination import CustomPagination
from urllib.parse import urlparse


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
                IsDomainExists,
                IsUrlLessThanAllowed
            )
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        url_qs = self.request.user.company.url_set.filter(domain_id=self.kwargs['domain_id'])

        if self.request.GET.get('search'):
            url_qs = url_qs.filter(
                Q(url__icontains=self.request.GET['search']) |
                Q(urllabel__label__icontains=self.request.GET['search']) |
                Q(last_ping_status_code__startswith=self.request.GET['search'])
            ).distinct()

        if self.request.GET.get('ordering') == 'url' or self.request.GET.get('ordering') == '-url':
            url_qs = url_qs.order_by(self.request.GET['ordering'])

        return url_qs

    def get_paginated_response(self):
        page = self.paginate_queryset(self.get_queryset(), self.request)
        serializer = UrlSerializer(page, many=True, context={'request': self.request})
        return super().get_paginated_response(serializer.data)

    def set_total_urls(self, response_data):
        response_data['total_urls'] = self.request.user.company.url_set.count()
        return response_data

    def get(self, request, domain_id):
        if 'no_paginate' in request.GET:
            serializer = UrlSerializer(self.get_queryset(), many=True, context={'request': request})
            response = Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response = self.get_paginated_response()
        self.set_total_urls(response.data)
        return response

    def post(self, request, domain_id):
        request_data = request.data.copy()
        request_data.update({'company': request.user.company.id, 'domain': domain_id})
        serializer = UrlCreateSerializer(data=request_data)
        if serializer.is_valid():
            serializer = UrlSerializer(serializer.save(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UrlDetailView(APIView):
    http_method_names = ('get', 'patch', 'delete')
    permission_classes = (IsAuthenticated, IsTrialActiveOrSubscribed, IsUrlExists)
    authentication_classes = (JWTAuthentication,)

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


class UrlRequestFileView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated, IsTrialActiveOrSubscribed, IsDomainExists)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, domain_id):
        serializer = UrlRequestFileSerializer(data=request.data)
        if serializer.is_valid():
            request.user.company.generate_downloadable_file_token()
            uidb64 = urlsafe_base64_encode(force_bytes(request.user.company.id))
            token = request.user.company.downloadable_file_token
            uri = urlparse(request.build_absolute_uri())

            response_data = {
                'download_link': f'{uri.scheme}://{uri.netloc}{reverse("urls:export", kwargs={"domain_id": domain_id})}?uidb64={uidb64}&token={token}&export_format={serializer.validated_data["format"]}'
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UrlExportView(APIView):
    http_method_names = ('get',)
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, domain_id):
        request_data = {
            'uidb64': request.GET.get('uidb64'),
            'token': request.GET.get('token'),
            'export_format': request.GET.get('export_format'),
            'domain': domain_id,
        }
        serializer = UrlExportSerializer(data=request_data)
        if serializer.is_valid():
            company = serializer.get_company()
            company.clear_downloadable_file_token()
            domain = serializer.validated_data['domain']
            return export_to_csv(domain) if serializer.validated_data['export_format'] == 'csv' else export_to_xls(domain)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
