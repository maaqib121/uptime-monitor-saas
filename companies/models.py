from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from pytz import timezone
from math import ceil


def logo_upload_path(instance, filename):
    return f'companies/{instance.name}/{filename}'


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to=logo_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    google_refresh_token = models.TextField(null=True, blank=True)
    linked_google_email = models.EmailField(null=True, blank=True)
    downloadable_file_token = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name

    def generate_downloadable_file_token(self):
        self.downloadable_file_token = get_random_string(length=32)
        self.save()

    def clear_downloadable_file_token(self):
        self.downloadable_file_token = None
        self.save()

    def set_stripe_customer_id(self, stripe_customer_id):
        self.stripe_customer_id = stripe_customer_id
        self.save()

    def set_stripe_subscription_id(self, stripe_subscription_id):
        self.stripe_subscription_id = stripe_subscription_id
        self.save()

    def set_subscribed_plan(self, subscribed_plan):
        self.subscribed_plan = subscribed_plan
        self.save()

    def clear_linked_google_account(self):
        self.google_refresh_token = None
        self.linked_google_email = None
        self.save()

    @property
    def remaining_trail_days(self):
        return ceil((self.created_at + timedelta(days=7) - datetime.now(tz=timezone(settings.TIME_ZONE))).total_seconds() / (60 * 60 * 24))
