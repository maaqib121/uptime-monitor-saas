from rest_framework import serializers
from rest_framework.fields import empty
from companies.models import Company
from users.models import User
from plans.api.v1.serializers import PriceSerializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ('stripe_customer_id', 'stripe_subscription_id')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['statistics'] = serializers.SerializerMethodField()
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

    def get_statistics(self, instance):
        return {
            'total_users': User.objects.filter(profile__company=instance).count(),
            'total_domains': instance.domain_set.count(),
            'total_urls': instance.url_set.count()
        }


class CompanyQuotationSerializer(serializers.Serializer):
    allowed_users = serializers.IntegerField(min_value=1)
    allowed_domains = serializers.IntegerField(min_value=1)
    allowed_urls = serializers.IntegerField(min_value=1)
    ping_interval = serializers.IntegerField(min_value=1)
    body = serializers.CharField()
