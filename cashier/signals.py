# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

# local
from .models import CashCount, Booking


@receiver(post_save, sender=CashCount)
def make_cashcount_bookings(sender, instance, **kwargs):
    if not instance.booking:
        # add booking
        newbooking = Booking.objects.create(
            booking_type=Booking.COUNT,
            journal=instance.journal,
            account=instance.journal.number,
            amount=instance.total,
            text=instance.__str__())
        CashCount.objects.filter(pk=instance.pk).update(booking=newbooking)
