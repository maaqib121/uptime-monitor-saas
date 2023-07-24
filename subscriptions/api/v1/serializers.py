from rest_framework import serializers
from companies.models import Company
from plans.models import Price
from domains.models import Domain


class SubscriptionSerializer(serializers.Serializer):
    plan_price = serializers.PrimaryKeyRelatedField(queryset=Price.objects.all())
    domain = serializers.PrimaryKeyRelatedField(queryset=Domain.objects.all())
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    def validate(self, attrs):
        if attrs['plan_price'].company != None and attrs['plan_price'].company != attrs['company']:
            raise serializers.ValidationError({'plan_price': 'Cannot link this plan with your company.'})
        if attrs['domain'].subscribed_plan == attrs['plan_price']:
            raise serializers.ValidationError({'plan_price': 'Already subscribed.'})
        return super().validate(attrs)
