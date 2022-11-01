from django.db import models


class Plan(models.Model):
    class Frequency(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'

    title = models.CharField(max_length=100)
    frequency = models.CharField(max_length=7, choices=Frequency.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
