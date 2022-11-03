from django.db import models


class Plan(models.Model):
    title = models.CharField(max_length=100)
    allowed_users = models.PositiveIntegerField()
    allowed_domains = models.PositiveIntegerField()
    allowed_urls = models.PositiveIntegerField()


class Price(models.Model):
    class Frequency(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=7, choices=Frequency.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
