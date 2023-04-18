from rest_framework import serializers
from rest_framework.fields import empty
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password as is_password_valid
from django.conf import settings
from companies.models import Company
from users.models import User, Profile
from datetime import datetime
from pytz import timezone
import requests


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
        company = Company.objects.create(name=company_name, created_by=user)
        Profile.objects.create(company=company, user=user, first_name=first_name, last_name=last_name, is_company_admin=True)
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
        fields = ('id', 'email', 'phone_number', 'is_phone_verified')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            self.fields['profile'] = ProfileSerializer()
            self.fields['is_password_set'] = serializers.SerializerMethodField()
        else:
            self.fields.pop('is_phone_verified')
            if self.instance:
                self.fields.pop('email')
                self.fields.pop('phone_number')
                self.fields['is_company_admin'] = serializers.BooleanField()
            else:
                self.profile_serializer = None
                self.fields['profile'] = serializers.JSONField()
                self.fields['redirect_uri'] = serializers.URLField()

    def get_is_password_set(self, instance):
        return not not (instance.password and instance.has_usable_password())

    def validate_profile(self, value):
        value['company'] = self.context['company'].id
        if self.initial_data.get('profile_pic'):
            value['profile_pic'] = self.initial_data['profile_pic']
        self.profile_serializer = ProfileSerializer(data=value)
        if not self.profile_serializer.is_valid():
            raise serializers.ValidationError(self.profile_serializer.errors)
        return value

    def validate_is_company_admin(self, value):
        if (
            not value and
            self.context['user'] != self.instance and
            self.context['user'].company.created_by == self.instance and
            self.instance.is_company_admin
        ):
            raise serializers.ValidationError('You cannot make company creator as non-admin.')
        return value

    def validate(self, attrs):
        if (
            'is_company_admin' in attrs and
            not attrs['is_company_admin'] and
            self.context['user'] == self.instance and
            self.context['user'].company_members().filter(profile__is_company_admin=True).count() == 1
        ):
            raise serializers.ValidationError('You are the only company admin. Assign anyone else before quitting this role.')
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('redirect_uri')
        validated_data.pop('profile')
        validated_data['is_active'] = True
        user = super().create(validated_data)
        self.profile_serializer.validated_data['user'] = user
        self.profile_serializer.save()
        return user

    def update(self, instance, validated_data):
        if 'is_company_admin' in validated_data:
            profile = instance.profile
            profile.is_company_admin = validated_data['is_company_admin']
            profile.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user',)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if data == empty:
            if 'company' in self.context:
                from companies.api.v1.serializers import CompanySerializer
                self.fields['company'] = CompanySerializer()
        else:
            if self.instance:
                self.fields.pop('company')
                self.fields['phone_number'] = serializers.CharField()

    def update(self, instance, validated_data):
        if validated_data.get('phone_number') != instance.user.phone_number:
            self.instance.user.set_phone_number(validated_data.pop('phone_number'))
        return super().update(instance, validated_data)


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


class UserSendPasswordSerializer(serializers.Serializer):
    redirect_uri = serializers.URLField()


class RequestPhoneOtpSerializer(serializers.Serializer):
    def validate(self, attrs):
        if not self.context['user'].phone_number:
            raise serializers.ValidationError('Phone number not set.')

        if self.context['user'].is_phone_verified:
            raise serializers.ValidationError('Phone number already verified.')

        return super().validate(attrs)


class PhoneVerifySerializer(serializers.Serializer):
    otp = serializers.CharField()

    def validate(self, attrs):
        if attrs['otp'] != self.context['user'].phone_otp:
            raise serializers.ValidationError({'otp': 'Invalid OTP.'})

        if self.context['user'].phone_otp_expiry_date < datetime.now(timezone('UTC')):
            raise serializers.ValidationError('OTP has been expired.')

        return super().validate(attrs)
