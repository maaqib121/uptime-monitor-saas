from django.db import models


class Plan(models.Model):
    title = models.CharField(max_length=100)
    allowed_users = models.PositiveIntegerField()
    allowed_domains = models.PositiveIntegerField()
    allowed_urls = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Price(models.Model):
    class Frequency(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=7, choices=Frequency.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.plan} {self.get_frequency_display()} - {self.amount}'
