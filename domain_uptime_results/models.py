from django.db import models
from companies.models import Company
from domains.models import Domain


class DomainUptimeResult(models.Model):
    class Status(models.TextChoices):
        UP = 'up', 'Up'
        DOWN = 'down', 'Down'

    status = models.CharField(max_length=4, choices=Status.choices)
    ssl_validity = models.DateTimeField()
    status_code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
