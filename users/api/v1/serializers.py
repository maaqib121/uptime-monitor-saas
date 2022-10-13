from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth.password_validation import validate_password as is_password_valid
from companies.models import Company
from users.models import User, Profile


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    company_name = serializers.CharField()
    redirect_uri = serializers.URLField()

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'company_name', 'redirect_uri')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.redirect_uri = None

    def get_redirect_uri(self):
        return self.redirect_uri

    def validate_password(self, value):
        is_password_valid(value)
        return value

    def validate_password2(self, value):
        if self.initial_data['password'] != value:
            raise serializers.ValidationError('Password fields didn\'t match.')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        self.redirect_uri = validated_data.pop('redirect_uri')
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


class AuthenticateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = None

    def get_user(self):
        return self.user

    def validate(self, attrs):
        self.user = User.objects.filter(email=attrs['email']).first()
        if not self.user or not self.user.check_password(attrs['password']):
            raise serializers.ValidationError('Password incorrect or user does not exist.')

        if not self.user.is_active:
            raise serializers.ValidationError('User inactive.')

        if not self.user:
            raise serializers.ValidationError('Invalid credentials.')

        return super().validate(attrs)


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
