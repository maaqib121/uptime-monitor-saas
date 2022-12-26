from rest_framework import serializers
from rest_framework.fields import empty
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from companies.models import Company
from domains.models import Domain
from urls.models import Url, UrlLabel
from urllib.parse import urlparse
from datetime import datetime
from pytz import timezone


class UrlLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlLabel
        exclude = ('url',)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data != empty:
            self.fields['id'] = serializers.IntegerField(label='ID', required=False)
            self.fields['delete'] = serializers.BooleanField(required=False)


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = '__all__'
        extra_kwargs = {
            'url': {
                'error_messages': {
                    'invalid': 'Invalid URL format.'
                },
            }
        }

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['labels'] = UrlLabelSerializer(source='urllabel_set', many=True)
        else:
            self.fields.pop('company')
            self.fields.pop('domain')
            self.fields.pop('last_ping_status_code')
            self.fields.pop('last_alert_date_time')
            if self.instance:
                self.fields.pop('url')
                self.fields['labels'] = serializers.JSONField(required=False)
                self.label_serializer = None

    def validate_url(self, value):
        url_id = self.instance.id if self.instance else None
        domain = self.context['domain'] if self.context.get('domain') else self.instance.domain
        if Url.objects.filter(url=value, domain=domain).exclude(id=url_id).exists():
            raise serializers.ValidationError('Must be unique for a domain.')
        return value

    def validate_labels(self, value):
        self.label_serializer = UrlLabelSerializer(data=value, many=True)
        if not self.label_serializer.is_valid():
            raise serializers.ValidationError(self.label_serializer.errors)
        return value

    def validate(self, attrs):
        domain = self.context['domain'] if self.context.get('domain') else self.instance.domain
        if attrs.get('url') and urlparse(attrs['url']).netloc != urlparse(domain.domain_url).netloc:
            raise serializers.ValidationError({'url': 'URL not maching with the domain.'})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('labels', [])
        validated_data.update({'company':  self.context['company'], 'domain': self.context['domain']})
        url = super().create(validated_data)
        if self.label_serializer:
            url_labels = []
            for url_label in self.label_serializer.validated_data:
                url_labels.append(UrlLabel(url=url, label=url_label['label']))
            UrlLabel.objects.bulk_create(url_labels)
        return url

    def update(self, instance, validated_data):
        validated_data.pop('labels', [])

        if self.label_serializer:
            new_url_labels = []
            url_labels = []
            removable_url_labels = []

            for url_label in self.label_serializer.validated_data:
                if 'id' in url_label and url_label.get('delete'):
                    removable_url_labels.append(url_label['id'])
                elif 'id' in url_label:
                    url_labels.append(UrlLabel(id=url_label['id'], label=url_label['label'],))
                else:
                    new_url_labels.append(UrlLabel(url=instance, label=url_label['label']))

            UrlLabel.objects.bulk_create(new_url_labels)
            UrlLabel.objects.bulk_update(url_labels, fields=['label'])
            UrlLabel.objects.filter(id__in=removable_url_labels).delete()

        return super().update(instance, validated_data)


class UrlCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        exclude = ('url', 'last_ping_status_code', 'last_alert_date_time')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['urls'] = serializers.JSONField()
        self.url_serializer = None
        self.fields['labels'] = serializers.JSONField(required=False)
        self.label_serializer = None

    def validate_labels(self, value):
        self.label_serializer = UrlLabelSerializer(data=value, many=True)
        if not self.label_serializer.is_valid():
            raise serializers.ValidationError(self.label_serializer.errors)
        return value

    def validate(self, attrs):
        if attrs['company'].url_set.count() + len(attrs['urls']) > attrs['company'].allowed_urls:
            raise serializers.ValidationError(
                f'Only {attrs["company"].allowed_urls} urls can be added in your company in current subscribed plan. '
                'Upgrade your plan to add more urls.'
            )
        self.url_serializer = UrlSerializer(
            data=attrs['urls'],
            many=True,
            context={'company': attrs['company'], 'domain': attrs['domain']}
        )
        if not self.url_serializer.is_valid():
            for error in self.url_serializer.errors:
                if error.get('url'):
                    raise serializers.ValidationError({'urls': (f'One or more URLs are invalid. Error: {str(error["url"][0])}')})
        return super().validate(attrs)

    def create(self, validated_data):
        urls = []
        for url in self.url_serializer.validated_data:
            urls.append(Url(url=url['url'], domain=validated_data['domain'], company=validated_data['company']))
        urls = Url.objects.bulk_create(urls)

        url_labels = []
        for url in urls:
            for label in self.label_serializer.validated_data:
                url_labels.append(UrlLabel(url=url, label=label['label']))
        UrlLabel.objects.bulk_create(url_labels)

        return urls


class UrlRequestFileSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['csv', 'xls'])


class UrlExportSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    domain = serializers.PrimaryKeyRelatedField(queryset=Domain.objects.all())
    export_format = serializers.ChoiceField(choices=['csv', 'xls'])

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.company = None

    def get_company(self):
        return self.company

    def validate(self, attrs):
        company = Company.objects.filter(id=urlsafe_base64_decode(attrs['uidb64']).decode()).first()
        if not company or company.downloadable_file_token != attrs['token']:
            raise serializers.ValidationError('Invalid token.')
        if attrs['domain'].company != company:
            raise serializers.ValidationError('Does not belong to this company.')

        self.company = company
        return super().validate(attrs)
