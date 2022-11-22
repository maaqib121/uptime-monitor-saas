from django.db import models
from countries.models import Country


class Domain(models.Model):
    domain_url = models.URLField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT)


class DomainLabel(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
