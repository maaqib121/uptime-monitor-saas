from rest_framework import serializers
from rest_framework.fields import empty
from django.conf import settings
from companies.models import Company
from users.models import User
import requests


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ('stripe_customer_id', 'google_refresh_token')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['statistics'] = serializers.SerializerMethodField()
            self.fields['remaining_trial_days'] = serializers.SerializerMethodField()
            if 'no_created_by' not in self.context:
                from users.api.v1.serializers import UserSerializer
                self.fields['created_by'] = UserSerializer()

    def get_remaining_trial_days(self, instance):
        return instance.remaining_trail_days

    def get_statistics(self, instance):
        total_urls = instance.url_set.filter(is_active=True).count()
        valid_urls = instance.url_set.filter(
            is_active=True,
            last_ping_status_code__gte=200,
            last_ping_status_code__lte=399
        ).count()
        return {
            'total_users': User.objects.filter(profile__company=instance).count(),
            'total_domains': instance.domain_set.filter(is_active=True).count(),
            'total_urls': total_urls,
            'last_health_score': round(valid_urls / total_urls * 100, 2) if total_urls else 0
        }


class CompanyQuotationSerializer(serializers.Serializer):
    allowed_users = serializers.IntegerField(min_value=1)
    allowed_urls = serializers.IntegerField(min_value=1)
    body = serializers.CharField()


class GoogleAuthenticateSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    redirect_uri = serializers.URLField()

    class Meta:
        model = User
        fields = ('code', 'redirect_uri')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.google_refresh_token = None
        self.linked_google_email = None

    def validate(self, attrs):
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': attrs['code'],
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': attrs['redirect_uri'],
                'grant_type': 'authorization_code'
            }
        )
        if response.status_code != 200:
            raise serializers.ValidationError(response.json()['error'])

        scopes = response.json()['scope'].split(' ')
        if 'https://www.googleapis.com/auth/analytics.readonly' not in scopes:
            raise serializers.ValidationError('Google Analytics permission must be granted.')

        self.google_refresh_token = response.json()['refresh_token']
        response = requests.get(
            'https://www.googleapis.com/userinfo/v2/me',
            headers={'Authorization': f"Bearer {response.json()['access_token']}"}
        )
        if response.status_code != 200:
            raise serializers.ValidationError(response.json()['error'])

        self.linked_google_email = response.json()['email']
        return super().validate(attrs)

    def update(self, instance, validated_data):
        validated_data.pop('code')
        validated_data.pop('redirect_uri')
        validated_data['google_refresh_token'] = self.google_refresh_token
        validated_data['linked_google_email'] = self.linked_google_email
        return super().update(instance, validated_data)


class GoogleDissociateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ()

    def validate(self, attrs):
        if not self.instance.linked_google_email:
            raise serializers.ValidationError('No google account is linked with your account.')
        response = requests.post('https://oauth2.googleapis.com/revoke', {
            'token': self.instance.google_refresh_token,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET
        })
        if response.status_code != 200:
            raise serializers.ValidationError(response.json()['error'])
        return super().validate(attrs)

    def update(self, instance, validated_data):
        validated_data['google_refresh_token'] = None
        validated_data['linked_google_email'] = None
        return super().update(instance, validated_data)
