from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, EventUserWishList

@receiver(post_save, sender=Event)
def update_wishlist_status(sender, instance, **kwargs):
    if instance.status == 'completed':
        EventUserWishList.objects.filter(event=instance).update(status='completed')
