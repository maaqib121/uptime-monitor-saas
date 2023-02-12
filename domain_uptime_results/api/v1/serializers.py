from rest_framework import serializers
from domain_uptime_results.models import DomainUptimeResult


class DomainUptimeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainUptimeResult
        exclude = ('domain',)
