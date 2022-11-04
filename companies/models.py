from django.db import models
from plans.models import Price


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
