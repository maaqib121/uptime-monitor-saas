from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from ping_results.models import PingResult
from datetime import datetime, timedelta
from domains.permissions import IsDomainExists
from urls.permissions import IsUrlExists


class PingHistoryView(APIView):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated, IsDomainExists, IsUrlExists)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        self.to_date = datetime.now().date()
        self.from_date = self.to_date - timedelta(days=31)
        return PingResult.objects.filter(
            company=self.request.user.company,
            url_id=self.kwargs['url_id'],
            created_at__date__gte=self.from_date,
            created_at__date__lte=self.to_date
        )

    def get(self, request, domain_id, url_id):
        ping_result_qs = self.get_queryset()
        response_data = []

        while self.from_date < self.to_date:
            result = {
                str(self.from_date): [
                    {'name': '200', 'count': 0},
                    {'name': '3xx', 'count': 0},
                    {'name': '4xx', 'count': 0},
                    {'name': '5xx', 'count': 0}
                ]
            }

            for ping_result in ping_result_qs:
                if ping_result.created_at.date() >= self.from_date:
                    if ping_result.status_code == 200:
                        result[str(self.from_date)][0]['count'] += 1
                    elif ping_result.status_code >= 300 and ping_result.status_code <= 399:
                        result[str(self.from_date)][1]['count'] += 1
                    elif ping_result.status_code >= 400 and ping_result.status_code <= 499:
                        result[str(self.from_date)][2]['count'] += 1
                    elif ping_result.status_code >= 500 and ping_result.status_code <= 599:
                        result[str(self.from_date)][3]['count'] += 1

            response_data.append(result)
            self.from_date += timedelta(days=1)

        return Response(response_data, status=status.HTTP_200_OK)


class HealthRateView(APIView):
    http_method_names = ('get',)
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if 'url_id' in self.kwargs:
            permission_classes = (IsAuthenticated, IsDomainExists, IsUrlExists)
        elif 'domain_id' in self.kwargs:
            permission_classes = (IsAuthenticated, IsDomainExists)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        self.to_date = datetime.now().date()
        self.from_date = self.to_date - timedelta(days=31)
        ping_result_qs = PingResult.objects.filter(
            company=self.request.user.company,
            created_at__date__gte=self.from_date,
            created_at__date__lte=self.to_date
        )
        if 'domain_id' in self.kwargs:
            ping_result_qs = ping_result_qs.filter(url__domain_id=self.kwargs['domain_id'])

        if 'url_id' in self.kwargs:
            ping_result_qs = ping_result_qs.filter(url_id=self.kwargs['url_id'])

        return ping_result_qs

    def get(self, request, *args, **kwargs):
        ping_result_qs = self.get_queryset()
        response_data = {}
        while self.from_date < self.to_date:
            success_results_count = ping_result_qs.filter(created_at__date=self.from_date, status_code=200).count()
            total_results_count = ping_result_qs.filter(created_at__date=self.from_date).count()
            response_data.update({
                str(self.from_date): success_results_count / total_results_count * 100 if total_results_count != 0 else 0
            })
            self.from_date += timedelta(days=1)

        return Response(response_data, status=status.HTTP_200_OK)
