from rest_framework import serializers
from rest_framework.fields import empty
from urls.models import Url, UrlLabel


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

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['labels'] = UrlLabelSerializer(source='urllabel_set', many=True)
        else:
            self.fields['labels'] = serializers.JSONField(required=False)
            self.label_serializer = None

    def validate_labels(self, value):
        self.label_serializer = UrlLabelSerializer(data=value, many=True)
        if not self.label_serializer.is_valid():
            raise serializers.ValidationError(self.label_serializer.errors)
        return value

    def create(self, validated_data):
        validated_data.pop('labels', [])
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
