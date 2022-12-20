from rest_framework import serializers
from rest_framework.fields import empty
from users.models import User
from domains.models import Domain, DomainLabel
from users.api.v1.serializers import UserSerializer
from countries.api.v1.serializers import CountrySerializer
from urllib.parse import urlparse


class DomainLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainLabel
        exclude = ('domain',)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data != empty:
            self.fields['id'] = serializers.IntegerField(label='ID', required=False)
            self.fields['delete'] = serializers.BooleanField(required=False)


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['labels'] = DomainLabelSerializer(source='domainlabel_set', many=True)
            self.fields['users'] = UserSerializer(many=True)
            self.fields['country'] = CountrySerializer()
            self.fields['total_urls'] = serializers.SerializerMethodField()
        else:
            self.fields['labels'] = serializers.JSONField(required=False)
            self.label_serializer = None

    def get_total_urls(self, instance):
        return instance.url_set.count()

    def validate_domain_url(self, value):
        uri = urlparse(value)
        if value != f'{uri.scheme}://{uri.netloc}':
            raise serializers.ValidationError('Must be domain only.')
        if self.instance and self.instance.domain_url != value and self.instance.url_set.exists():
            raise serializers.ValidationError('Cannot be updated since URLs across this domain already exists.')
        return value

    def validate_labels(self, value):
        self.label_serializer = DomainLabelSerializer(data=value, many=True)
        if not self.label_serializer.is_valid():
            raise serializers.ValidationError(self.label_serializer.errors)
        return value

    def validate(self, attrs):
        domain_id = self.instance.id if self.instance else None
        domain_url = attrs['domain_url'] if attrs.get('domain_url') else self.instance.domain_url
        country = attrs['country'] if attrs.get('country') else self.instance.country
        company = attrs['company'] if attrs.get('company') else self.instance.company

        if (
            (attrs.get('domain_url') or attrs.get('country')) and
            Domain.objects.filter(domain_url=domain_url, country=country).exclude(id=domain_id).exists()
        ):
            raise serializers.ValidationError({'domain_url': 'Must be unique for a country.'})

        user_ids = [user.id for user in attrs.get('users', [])]
        if user_ids and User.objects.filter(id__in=user_ids, profile__company=company).count() != len(attrs['users']):
            raise serializers.ValidationError({'users': 'One or more user does not exists.'})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('labels', [])
        domain = super().create(validated_data)
        if self.label_serializer:
            domain_labels = []
            for domain_label in self.label_serializer.validated_data:
                domain_labels.append(DomainLabel(domain=domain, label=domain_label['label'],))
            DomainLabel.objects.bulk_create(domain_labels)
        return domain

    def update(self, instance, validated_data):
        validated_data.pop('labels', [])

        if self.label_serializer:
            new_domain_labels = []
            domain_labels = []
            removable_domain_labels = []

            for domain_label in self.label_serializer.validated_data:
                if 'id' in domain_label and domain_label.get('delete'):
                    removable_domain_labels.append(domain_label['id'])
                elif 'id' in domain_label:
                    domain_labels.append(DomainLabel(id=domain_label['id'], label=domain_label['label']))
                else:
                    new_domain_labels.append(DomainLabel(domain=instance, label=domain_label['label']))

            DomainLabel.objects.bulk_create(new_domain_labels)
            DomainLabel.objects.bulk_update(domain_labels, fields=['label'])
            DomainLabel.objects.filter(id__in=removable_domain_labels).delete()

        return super().update(instance, validated_data)
