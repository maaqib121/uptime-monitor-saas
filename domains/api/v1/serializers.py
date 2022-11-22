from rest_framework import serializers
from rest_framework.fields import empty
from domains.models import Domain, DomainLabel


class DomainLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainLabel
        exclude = ('domain',)


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
