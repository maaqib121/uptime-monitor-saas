from django.db import models
from companies.models import Company
from domains.models import Domain


class Invoice(models.Model):
    stripe_invoice_id = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    invoice_url = models.URLField()
    created_at = models.DateTimeField()
