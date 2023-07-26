from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from domain_uptime_results.models import DomainUptimeResult
from datetime import datetime, timedelta
from domains.permissions import IsDomainActive


class DomainUptimeHistoryView(APIView):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated, IsDomainActive)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        self.to_date = datetime.now().date()
        self.from_date = self.to_date - timedelta(days=31)
        return DomainUptimeResult.objects.filter(
            company=self.request.user.company,
            domain_id=self.kwargs['domain_id'],
            created_at__date__gte=self.from_date,
            created_at__date__lte=self.to_date
        )

    def get(self, request, domain_id):
        domain_uptime_result_qs = self.get_queryset()
        response_data = []

        while self.from_date <= self.to_date:
            result = {
                'uptime_percentage': 0,
                'uptime_duration_minutes': 0,
                'downtime_duration_minutes': 0
            }
            for domain_uptime_result in domain_uptime_result_qs.filter(created_at__date=self.from_date):
                if domain_uptime_result.status == DomainUptimeResult.Status.UP:
                    result['uptime_duration_minutes'] += 1
                else:
                    result['downtime_duration_minutes'] += 1

            total_minutes = result['uptime_duration_minutes'] + result['downtime_duration_minutes']
            result['uptime_percentage'] = result['uptime_duration_minutes'] / total_minutes * 100 if total_minutes else 0
            response_data.append({str(self.from_date): result})
            self.from_date += timedelta(days=1)

        return Response(response_data, status=status.HTTP_200_OK)
