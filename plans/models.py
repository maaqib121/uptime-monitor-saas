from django.db import models
from django.core import exceptions


class Plan(models.Model):
    title = models.CharField(max_length=100)
    allowed_urls = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, null=True, blank=True)
    stripe_product_id = models.CharField(max_length=100, null=True, blank=True)

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

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.plan} {self.get_frequency_display()} - {self.amount}'

    def clean(self):
        if Price.objects.filter(plan=self.plan, frequency=self.frequency).exclude(id=self.id).exists():
            raise exceptions.ValidationError(f'{self.get_frequency_display()} price already exists against this plan.')
        return super().clean()

    @property
    def company(self):
        return self.plan.company

    @property
    def allowed_urls(self):
        return self.plan.allowed_urls
