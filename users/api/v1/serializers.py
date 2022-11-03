from rest_framework import serializers
from rest_framework.fields import empty
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password as is_password_valid
from django.conf import settings
from companies.models import Company
from users.models import User, Profile
from companies.api.v1.serializers import CompanySerializer
from datetime import datetime
from pytz import timezone


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

    def validate_company_name(self, value):
        if Company.objects.filter(name=value).exists():
            raise serializers.ValidationError('Name already taken')
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


class UserConfirmationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = None

    def get_user(self):
        return self.user

    def validate(self, attrs):
        user = User.objects.filter(id=urlsafe_base64_decode(attrs['uidb64']).decode()).first()
        if not user or user.confirmation_token != attrs['token']:
            raise serializers.ValidationError('Invalid confirmation token.')

        if user.confirmation_token_expiry_date < datetime.now(tz=timezone(settings.TIME_ZONE)):
            raise serializers.ValidationError('Confirmation token has been expired.')

        self.user = user
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

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['company'] = CompanySerializer()
        else:
            self.fields.pop('company')


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    redirect_uri = serializers.URLField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = None

    def get_user(self):
        return self.user

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError('No user exists against this email address.')
        if not user.is_active:
            raise serializers.ValidationError('User inactive.')
        self.user = user
        return value


class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = None

    def get_user(self):
        return self.user

    def validate(self, attrs):
        user = User.objects.filter(id=urlsafe_base64_decode(attrs['uidb64']).decode()).first()
        if not user or user.confirmation_token != attrs['token']:
            raise serializers.ValidationError('Invalid password reset token.')

        if user.confirmation_token_expiry_date < datetime.now(tz=timezone('UTC')):
            raise serializers.ValidationError('Reset Password token has been expired.')

        try:
            is_password_valid(attrs['password'])
        except Exception as exception:
            error_list = []
            for exception in exception.error_list:
                if exception.params:
                    exception.message = exception.message % {list(exception.params.keys())[0]: list(exception.params.values())[0]}
                error_list.append(exception.message)
            raise serializers.ValidationError({'password': error_list})

        if self.initial_data['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Password fields didn\'t match.'})

        self.user = user
        return super().validate(attrs)
