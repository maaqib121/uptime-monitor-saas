from rest_framework import serializers
from rest_framework.fields import empty
from plans.models import Plan, Price


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        exclude = ('plan', 'stripe_price_id')


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['prices'] = PriceSerializer(source='price_set', many=True)
