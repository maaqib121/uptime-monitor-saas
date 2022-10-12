from rest_framework import serializers
from rest_framework.fields import empty
from companies.models import Company
from users.models import User, Profile


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    company_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'company_name')

    def validate_password2(self, value):
        if self.initial_data['password'] != value:
            raise serializers.ValidationError('Password fields didn\'t match.')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        company_name = validated_data.pop('company_name')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        company = Company.objects.create(name=company_name)
        Profile.objects.create(company=company, user=user, first_name=first_name, last_name=last_name)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields['profile'] = ProfileSerializer()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user',)
