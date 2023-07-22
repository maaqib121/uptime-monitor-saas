from django.db import models
from django.core import exceptions
from django.contrib.postgres.fields import ArrayField
from pingApi.constants import TRIAL_ALLOWED_URLS
from countries.models import Country
from companies.models import Company
from users.models import User
from urllib.parse import urlparse
from plans.models import Price


class Domain(models.Model):
    domain_url = models.URLField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, blank=True)
    alert_emails = ArrayField(models.EmailField(), null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    subscribed_plan = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    is_subscription_active = models.BooleanField(default=False)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.domain_url

    def clean(self):
        uri = urlparse(self.domain_url)
        if self.domain_url != f'{uri.scheme}://{uri.netloc}':
            raise exceptions.ValidationError({'domain_url': 'Must be domain only.'})

        if Domain.objects.filter(
            domain_url=self.domain_url,
            country=self.country,
            company=self.company
        ).exclude(id=self.id).exists():
            raise exceptions.ValidationError({'domain_url': 'Must be unique for a country.'})

        return super().clean()

    def set_stripe_subscription_id(self, stripe_subscription_id):
        self.stripe_subscription_id = stripe_subscription_id
        self.save()

    def start_subscription(self, subscribed_plan):
        self.is_subscription_active = True
        self.subscribed_plan = subscribed_plan
        self.is_trial_available = False
        self.save()

    def clear_subscription(self):
        self.is_subscription_active = False
        self.stripe_subscription_id = None
        self.subscribed_plan = None
        self.save()

    @property
    def allowed_urls(self):
        return self.subscribed_plan.allowed_users if self.subscribed_plan else TRIAL_ALLOWED_URLS


class DomainLabel(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.domain} - {self.label}'
