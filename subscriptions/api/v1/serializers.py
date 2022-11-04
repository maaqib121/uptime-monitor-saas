from rest_framework import serializers
from plans.models import Price


class SubscriptionSerializer(serializers.Serializer):
    plan_price = serializers.PrimaryKeyRelatedField(queryset=Price.objects.all())
