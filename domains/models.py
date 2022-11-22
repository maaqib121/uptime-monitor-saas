from django.db import models
from countries.models import Country
from companies.models import Company


class Domain(models.Model):
    domain_url = models.URLField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class DomainLabel(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
