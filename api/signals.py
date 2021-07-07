from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import User, UserProfile


@receiver(post_save, sender=User)
def _create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            phone_number=instance.phone_number,
            name=instance.name,
            email=instance.email,
        )
