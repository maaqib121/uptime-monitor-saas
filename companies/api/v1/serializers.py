from rest_framework import serializers
from rest_framework.fields import empty
from django.conf import settings
from companies.models import Company
from datetime import datetime, timedelta
from pytz import timezone
from math import ceil


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['remaining_trial_days'] = serializers.SerializerMethodField()

    def get_remaining_trial_days(self, obj):
        return ceil((obj.created_at + timedelta(days=7) - datetime.now(tz=timezone(settings.TIME_ZONE))).total_seconds() / (60 * 60 * 24))
