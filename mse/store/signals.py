from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Organization
from .services import ensure_subscription

@receiver(post_save, sender=Organization)
def _org_subscription_bootstrap(sender, instance: Organization, created: bool, **kwargs):
    if created:
        ensure_subscription(instance)
