from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from companies.models import Company
from datetime import datetime, timedelta
import random


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email address cannot be null/blank.")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_admin = True
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=50, null=True, blank=True)
    confirmation_token_expiry_date = models.DateTimeField(null=True, blank=True)
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    phone_otp_expiry_date = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.email

    def generate_confirmation_token(self):
        self.confirmation_token = get_random_string(length=32)
        self.confirmation_token_expiry_date = datetime.now() + timedelta(days=7)
        self.save()

    def clear_confirmation_token(self):
        self.confirmation_token = None
        self.confirmation_token_expiry_date = None
        self.save()

    def generate_phone_otp(self):
        self.phone_otp = random.randint(100000, 999999)
        self.phone_otp_expiry_date = datetime.now() + timedelta(minutes=10)
        self.save()

    def clear_phone_otp(self):
        self.phone_otp = None
        self.phone_otp_expiry_date = None
        self.save()

    def activate(self):
        self.is_active = True
        self.save()

    def update_password(self, password):
        self.set_password(password)
        self.save()

    def set_phone_number(self, phone_number):
        self.phone_number = phone_number
        self.save()

    def company_members(self):
        return User.objects.filter(profile__company=self.company)

    @property
    def first_name(self):
        return self.profile.first_name

    @property
    def last_name(self):
        return self.profile.last_name

    @property
    def full_name(self):
        return self.profile.full_name

    @property
    def company(self):
        return self.profile.company

    @property
    def is_company_admin(self):
        return self.profile.is_company_admin


def profile_pic_upload_path(instance, filename):
    return f'users/{instance.user_id}/profile_pic/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_company_admin = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to=profile_pic_upload_path, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
