from django.db import models
from django.conf import settings
from pingApi.constants import TRIAL_ALLOWED_USERS, TRIAL_ALLOWED_DOMAINS, TRIAL_ALLOWED_URLS, TRIAL_PING_INTERVAL
from plans.models import Price
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
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    subscribed_plan = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    is_subscription_active = models.BooleanField(default=False)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name

    def set_stripe_customer_id(self, stripe_customer_id):
        self.stripe_customer_id = stripe_customer_id
        self.save()

    def set_stripe_subscription_id(self, stripe_subscription_id):
        self.stripe_subscription_id = stripe_subscription_id
        self.save()

    def set_subscribed_plan(self, subscribed_plan):
        self.subscribed_plan = subscribed_plan
        self.save()

    @property
    def allowed_users(self):
        return self.subscribed_plan.allowed_users if self.subscribed_plan else TRIAL_ALLOWED_USERS

    @property
    def allowed_domains(self):
        return self.subscribed_plan.allowed_users if self.subscribed_plan else TRIAL_ALLOWED_DOMAINS

    @property
    def allowed_urls(self):
        return self.subscribed_plan.allowed_users if self.subscribed_plan else TRIAL_ALLOWED_URLS

    @property
    def allowed_urls(self):
        return self.subscribed_plan.ping_interval if self.subscribed_plan else TRIAL_PING_INTERVAL

    @property
    def ping_interval(self):
        return self.subscribed_plan.ping_interval if self.subscribed_plan else TRIAL_PING_INTERVAL

    @property
    def remaining_trail_days(self):
        return ceil((self.created_at + timedelta(days=7) - datetime.now(tz=timezone(settings.TIME_ZONE))).total_seconds() / (60 * 60 * 24))
