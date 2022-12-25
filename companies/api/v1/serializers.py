from rest_framework import serializers
from rest_framework.fields import empty
from companies.models import Company
from plans.api.v1.serializers import PriceSerializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ('stripe_customer_id', 'stripe_subscription_id')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['remaining_trial_days'] = serializers.SerializerMethodField()
            self.fields['plan_restrictions'] = serializers.SerializerMethodField()
            self.fields['subscribed_plan'] = PriceSerializer()
            if 'no_created_by' not in self.context:
                from users.api.v1.serializers import UserSerializer
                self.fields['created_by'] = UserSerializer()

    def get_remaining_trial_days(self, instance):
        return instance.remaining_trail_days

    def get_plan_restrictions(self, instance):
        return {
            'allowed_users': instance.allowed_users,
            'allowed_domains': instance.allowed_domains,
            'allowed_urls': instance.allowed_urls,
            'ping_interval': instance.ping_interval
        }


class CompanyQuotationSerializer(serializers.Serializer):
    allowed_users = serializers.IntegerField()
    allowed_domains = serializers.IntegerField()
    allowed_urls = serializers.IntegerField()
    body = serializers.CharField()
