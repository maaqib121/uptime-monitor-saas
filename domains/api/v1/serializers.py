from rest_framework import serializers
from rest_framework.fields import empty
from domains.models import Domain, DomainLabel


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
        else:
            self.fields['labels'] = serializers.JSONField()
            self.label_serializer = None

    def validate_labels(self, value):
        self.label_serializer = DomainLabelSerializer(data=value, many=True)
        if not self.label_serializer.is_valid():
            raise serializers.ValidationError(self.label_serializer.errors)
        return value

    def create(self, validated_data):
        validated_data.pop('labels')
        domain = super().create(validated_data)
        domain_labels = []
        for domain_label in self.label_serializer.validated_data:
            domain_labels.append(DomainLabel(domain=domain, label=domain_label['label'],))
        DomainLabel.objects.bulk_create(domain_labels)
        return domain

    def update(self, instance, validated_data):
        validated_data.pop('labels', [])
        new_domain_labels = []
        domain_labels = []
        removable_domain_labels = []

        for domain_label in self.label_serializer.validated_data:
            if 'id' in domain_label and domain_label.get('delete'):
                removable_domain_labels.append(domain_label['id'])
            elif 'id' in domain_label:
                domain_labels.append(DomainLabel(id=domain_label['id'], label=domain_label['label'],))
            else:
                new_domain_labels.append(DomainLabel(domain=instance, label=domain_label['label']))

        DomainLabel.objects.bulk_create(new_domain_labels)
        DomainLabel.objects.bulk_update(domain_labels, fields=['label'])
        DomainLabel.objects.filter(id__in=removable_domain_labels).delete()

        return super().update(instance, validated_data)
