# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# local
from .models import Fablog


@receiver(post_save, sender=Fablog)
def make_fablog_bookings(sender, instance, **kwargs):
    if instance.dues() == 0:
        # make bookings for all positions
        pass
