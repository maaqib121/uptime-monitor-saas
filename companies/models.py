from enum import unique
from django.db import models


def logo_upload_path(instance, filename):
    return f'companies/{instance.name}/{filename}'


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to=logo_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
