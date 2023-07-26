from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q, Count
from domains.api.v1.serializers import DomainSerializer, DomainSelectSerializer
from domains.permissions import IsDomainExists
from pingApi.utils.pagination import CustomPagination


class DomainView(APIView, CustomPagination):
    http_method_names = ('get', 'post')
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

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

        if self.request.GET.get('is_active'):
            is_active = True if self.request['is_active'] == 'true' else False
            domain_qs = domain_qs.filter(is_active=is_active)

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
    permission_classes = (IsAuthenticated, IsDomainExists)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, domain_id):
        serializer = DomainSerializer(self.domain, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, domain_id):
        serializer = DomainSerializer(self.domain, data=request.data, partial=True, context={'company': request.user.company})
        if serializer.is_valid():
            serializer = DomainSerializer(serializer.save(), context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, domain_id):
        self.domain.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DomainSelectView(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        serializer = DomainSelectSerializer(data=request.data, context={'company': request.user.company})
        if serializer.is_valid():
            domains = serializer.save()
            context = {
                'no_labels': True,
                'no_users': True,
                'no_total_urls': True,
                'no_last_health_score': True,
                'no_last_uptime_result': True
            }
            response_data = {
                'selected_domains': DomainSerializer(domains['selected_domains'], many=True, context=context).data,
                'unselected_domains': DomainSerializer(domains['unselected_domains'], many=True, context=context).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
