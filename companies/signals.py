from django.db.models.signals import post_save
from django.dispatch import receiver
from companies.models import Company
from ping_results.tasks import ping


@receiver(post_save, sender=Company)
def start_ping(sender, instance, created, *args, **kwargs):
    if created:
        ping.delay(instance.id)
