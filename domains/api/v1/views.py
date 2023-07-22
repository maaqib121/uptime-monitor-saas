from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q, Count
from domains.models import Domain
from domains.api.v1.serializers import DomainSerializer
from domains.permissions import IsDomainExists, IsDomainLessThanAllowed
from pingApi.utils.pagination import CustomPagination


class DomainView(APIView, CustomPagination):
    http_method_names = ('get', 'post')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (IsAuthenticated, IsDomainLessThanAllowed)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        domain_qs = self.request.user.company.domain_set.all()

        if self.request.GET.get('search'):
            domain_qs = domain_qs.filter(
                Q(domain_url__icontains=self.request.GET['search']) |
                Q(domainlabel__label__icontains=self.request.GET['search'])
            ).distinct()

        if (
            self.request.GET.get('ordering') == 'domain_url' or self.request.GET.get('ordering') == '-domain_url' or
            self.request.GET.get('ordering') == 'total_urls' or self.request.GET.get('ordering') == '-total_urls'
        ):
            domain_qs = domain_qs.annotate(total_urls=Count('url')).order_by(self.request.GET['ordering'])

        return domain_qs

    def get_paginated_response(self):
        page = self.paginate_queryset(self.get_queryset(), self.request)
        serializer = DomainSerializer(page, many=True, context={'request': self.request})
        return super().get_paginated_response(serializer.data)

    def set_total_domains(self, response_data):
        response_data['total_domains'] = self.request.user.company.domain_set.count()
        return response_data

    def get(self, request):
        if 'no_paginate' in request.GET:
            serializer = DomainSerializer(self.get_queryset(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        response = self.get_paginated_response()
        self.set_total_domains(response.data)
        return response

    def post(self, request):
        request_data = request.data.copy()
        request_data['company'] = request.user.company.id
        serializer = DomainSerializer(data=request_data)
        if serializer.is_valid():
            serializer = DomainSerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DomainDetailView(APIView):
    http_method_names = ('get', 'patch', 'delete')
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = (IsAuthenticated, IsDomainExists)
        elif self.request.method == 'PATCH':
            permission_classes = (IsAuthenticated, IsDomainExists)
        else:
            permission_classes = (IsAuthenticated, IsDomainExists)
        return [permission() for permission in permission_classes]

    def get(self, request, domain_id):
        domain = Domain.objects.get(id=domain_id)
        serializer = DomainSerializer(domain, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, domain_id):
        domain = Domain.objects.get(id=domain_id)
        serializer = DomainSerializer(domain, data=request.data, partial=True, context={'company': request.user.company})
        if serializer.is_valid():
            serializer = DomainSerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, domain_id):
        domain = Domain.objects.get(id=domain_id)
        domain.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
