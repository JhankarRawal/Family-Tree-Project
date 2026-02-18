from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Person

@receiver([post_save, post_delete], sender=Person)
def clear_family_dashboard_cache(sender, instance, **kwargs):
    cache.clear()