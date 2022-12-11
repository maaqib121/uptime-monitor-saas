from django.db import models
from django.core import exceptions
from companies.models import Company
from domains.models import Domain
from urllib.parse import urlparse


class Url(models.Model):
    url = models.URLField()
    last_ping_status_code = models.PositiveIntegerField()
    last_ping_date_time = models.DateTimeField()
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.url

    def clean(self):
        if urlparse(self.url).netloc != urlparse(self.domain.domain_url).netloc:
            raise exceptions.ValidationError({'url': 'URL not maching with the domain.'})

        if Url.objects.filter(url=self.url, domain=self.domain).exclude(id=self.id).exists():
            raise exceptions.ValidationError({'url': 'Must be unique for a domain.'})

        return super().clean()

    def set_last_ping_status_code(self, status_code):
        self.last_ping_status_code = status_code
        self.save()


class UrlLabel(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.url} - {self.label}'
