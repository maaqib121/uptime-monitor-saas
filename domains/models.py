from django.db import models
from django.core import exceptions
from countries.models import Country
from companies.models import Company


class Domain(models.Model):
    domain_url = models.URLField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.domain_url

    def clean(self):
        if Domain.objects.filter(
            domain_url=self.domain_url,
                country=self.country,
                company=self.company
        ).exclude(id=self.id).exists():
            raise exceptions.ValidationError({'domain_url': 'Must be unique for a country.'})
        return super().clean()


class DomainLabel(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.domain} - {self.label}'
