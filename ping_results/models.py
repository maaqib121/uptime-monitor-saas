from django.db import models
from companies.models import Company
from urls.models import Url


class PingResult(models.Model):
    status_code = models.PositiveIntegerField()
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.url} ({self.status_code})'

    @property
    def domain(self):
        return self.url.domain
