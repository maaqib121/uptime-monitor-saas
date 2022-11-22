from django.db import models
from domains.models import Domain


class Url(models.Model):
    url = models.URLField()
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    def __str__(self):
        return self.url

    @property
    def company(self):
        return self.domain.company


class UrlLabel(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.url} - {self.label}'
