from rest_framework import serializers
from plans.models import Price


class SubscriptionSerializer(serializers.Serializer):
    plan_price = serializers.PrimaryKeyRelatedField(queryset=Price.objects.all())

    def validate_plan_price(self, value):
        if value.plan.company != None and value.plan.company != self.context['company']:
            raise serializers.ValidationError('Cannot link this plan with your company.')
        if self.context['company'].subscribed_plan == value:
            raise serializers.ValidationError('Already subscribed.')
        return value
