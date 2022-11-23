from django.db import models
from companies.models import Company
from domains.models import Domain


class Url(models.Model):
    url = models.URLField(unique=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.url


class UrlLabel(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.url} - {self.label}'
