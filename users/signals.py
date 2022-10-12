from django.db.models.signals import post_delete
from django.dispatch import receiver
from users.models import Profile


@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, *args, **kwargs):
    if instance.user:
        instance.user.delete()
