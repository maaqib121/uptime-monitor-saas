from rest_framework import serializers
from rest_framework.fields import empty
from urls.models import Url, UrlLabel


class UrlLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlLabel
        exclude = ('url',)


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = '__all__'

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['labels'] = UrlLabelSerializer(source='urllabel_set', many=True)
        else:
            self.fields['labels'] = serializers.JSONField()
            self.label_serializer = None

    def validate_labels(self, value):
        self.label_serializer = UrlLabelSerializer(data=value, many=True)
        if not self.label_serializer.is_valid():
            raise serializers.ValidationError(self.label_serializer.errors)
        return value

    def create(self, validated_data):
        validated_data.pop('labels', [])
        url = super().create(validated_data)
        url_labels = []
        for url_label in self.label_serializer.validated_data:
            url_labels.append(UrlLabel(url=url, label=url_label['label']))
        UrlLabel.objects.bulk_create(url_labels)
        return url
