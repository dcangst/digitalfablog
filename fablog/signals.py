# base
from operator import itemgetter

# Django
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from django.utils import timezone

# local
from .models import Fablog


@receiver(post_save, sender=Fablog)
def make_fablog_bookings(sender, instance, **kwargs):
    if instance.total() > 0 and instance.dues() == 0:
        # get Models
        Booking = apps.get_model('cashier', 'Booking')
        FablogBookings = apps.get_model('fablog', 'FablogBookings')

        # payments
        payments = instance.payments.all().order_by('-amount')
        # create list of fablog positions
        positions = instance.get_positions()
        positions.sort(key=itemgetter('amount'))
        # make bookings for all positions
        new_bookings = list()
        for payment in payments:
            amount = payment.amount
            while len(positions) > 0:
                if amount >= positions[-1]['amount']:
                    new_booking = Booking.objects.create(
                        booking_type=Booking.BOOKING,
                        journal=payment.payment_method.journal,
                        account=positions[-1]['account_to'],
                        amount=positions[-1]['amount'],
                        comment=positions[-1]['comment'])
                    new_bookings.append(new_booking)
                    amount = amount - positions[-1]['amount']
                    positions.pop()
                elif amount < positions[-1]['amount']:
                    positions[-1]['comment'] += " (part)"
                    new_booking = Booking.objects.create(
                        booking_type=Booking.BOOKING,
                        journal=payment.payment_method.journal,
                        account=positions[-1]['account_to'],
                        amount=amount,
                        comment=positions[-1]['comment'])
                    new_bookings.append(new_booking)
                    positions[-1]['amount'] = positions[-1]['amount'] - amount

        if settings.DEBUG:
            # check bookings - just for sanity
            total_bookings = sum([x.amount for x in new_bookings])
            total_payments = sum([x.amount for x in payments])
            assert total_bookings == total_payments

        # add bookings to fablog
        for booking in new_bookings:
            FablogBookings.objects.create(
                fablog=instance,
                booking=booking)

        # if a memebership was payed, add it to member model
        if instance.memberships.exists():
            Membership = apps.get_model('members', 'Membership')
            Membership.objects.create(
                member=instance.member,
                fablog=instance,
                # use first, because only on should be present. (as defined in the modelform)
                start_date=instance.fablogmemberships_set.first().start_date,
                end_date=instance.fablogmemberships_set.first().end_date)

        # set fablog to closed
        Fablog.objects.filter(pk=instance.pk).update(closed_at=timezone.now())
