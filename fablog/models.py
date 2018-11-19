# base
from datetime import timedelta, date
from decimal import Decimal
from math import ceil

# Django
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.urls import reverse


class Fablog(models.Model):
    """Fablog object"""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_fablogs",
        on_delete=models.PROTECT,
        verbose_name=_("Created by"),
        help_text=pgettext_lazy(
            "Fablog",
            "Labmanager who created the Fablog"))

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("created at"),
        help_text=pgettext_lazy(
            "Fablog",
            "Creation date and time"))

    # this is set to the last labmanager who took a payment. Fablogs are closed in post-save signal
    # when fablog.dues() is = 0.
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="closed_fablogs",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Closed by"),
        help_text=pgettext_lazy(
            "Fablog",
            "Labmanager who closed the Fablog"))

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("closed at"),
        help_text=pgettext_lazy(
            "Fablog",
            "Closure date and time"))

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="fablogs",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("member"),
        help_text=pgettext_lazy(
            "Fablog",
            "Member"))

    notes = models.TextField(
        blank=True,
        verbose_name=_("notes"),
        help_text=pgettext_lazy(
            "Fablog",
            "Notes on the Fablog"))

    fabday = models.ForeignKey(
        "FabDay",
        related_name="fablogs",
        verbose_name=_("fabday"),
        on_delete=models.PROTECT,
        help_text=pgettext_lazy(
            "Fablog",
            "FabDay of this Fablog"))

    machines = models.ManyToManyField(
        "machines.Machine",
        through="MachinesUsed",
        verbose_name=_("machines used"))

    varia = models.ManyToManyField(
        "fablog.Varia",
        through="FablogVaria",
        verbose_name=_("Various"))

    memberships = models.ManyToManyField(
        "members.MembershipType",
        through="FablogMemberships",
        verbose_name=_("Memberships"))

    donation = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        verbose_name=_('donation'),
        help_text=_('Donation to add to FabLog'))

    payments = models.ManyToManyField(
        "cashier.Payment",
        through="fablogPayments",
        verbose_name=_("Payments"))

    bookings = models.ManyToManyField(
        "cashier.Booking",
        through="fablogBookings",
        verbose_name=_("Bookings"))

    class Meta:
        verbose_name = _('fablog')
        verbose_name_plural = _('fablogs')
        ordering = ['-created_at', '-closed_at']

    def __str__(self):
        return self._meta.verbose_name + " " + str(self.id)

    def get_absolute_url(self):
        return reverse('fablog:detail', args=[str(self.id)])

    def total_machines(self):
        machines = self.machinesused_set.all()
        total_machine_costs = 0
        for machine in machines:
            total_machine_costs += machine.price()
        return total_machine_costs
    total_machines.short_description = _("subtotal machines")

    def total_varia(self):
        varia = self.fablogvaria_set.all()
        total_varia_costs = 0
        for var in varia:
            total_varia_costs += var.price()
        return total_varia_costs
    total_machines.short_description = _("subtotal varia")

    def total_memberships(self):
        memberships = self.fablogmemberships_set.all()
        total_membership_costs = 0
        for membership in memberships:
            total_membership_costs += membership.price()
        return total_membership_costs
    total_memberships.short_description = _("subtotal memberships")

    def total_payments(self):
        payments = self.fablogpayments_set.all()
        total_payments = 0
        for payment in payments:
            total_payments += payment.payment.amount
        return total_payments
    total_payments.short_description = _("total payments")

    def total_bookings(self):
        bookings = self.fablogbookings_set.all()
        total_bookings = 0
        for payment in bookings:
            total_bookings += payment.booking.amount
        return total_bookings
    total_bookings.short_description = _("total bookings")

    def total(self):
        return self.total_machines() + self.total_memberships() + self.total_varia()
    total.short_description = _("total overall")

    def dues(self):
        return self.total()-self.total_payments()
    dues.short_description = _("dues")

    def is_closed(self):
        if self.closed_at:
            return True
        else:
            return False

    def get_positions(self):
        """
        Get all positions in the fablog and return as a list.
        splits membership position according to year into multiple positions to allow for booking to
        different financial years
        """
        positions = list()

        # machines used
        machines_list = [{
            'contra_account': x.machine.contra_account,
            'amount': x.price(),
            'text': _('Usage fee {machine_name}').format(machine_name=x.machine.name)
            } for x in self.machinesused_set.all()]
        positions.extend(machines_list)

        # varia
        varia_list = [{
            'contra_account': x.varia.contra_account,
            'amount': x.price(),
            'text': x.booking_text()
            } for x in self.fablogvaria_set.all()]
        positions.extend(varia_list)

        # memberships (should only ever be one, but theoretically possible to have more)
        membership_list = []
        for m in self.fablogmemberships_set.all():
            end_date = m.end_date()
            if end_date.year > m.start_date.year:
                length_total = end_date - m.start_date
                length_thisperiod = date(year=m.start_date.year, month=12, day=31) - m.start_date
                price_thisperiod = round(Decimal(length_thisperiod / length_total) * m.price(), 0)
                price_nextperiod = m.price()-price_thisperiod
                # add position for this period
                membership_list.append({
                    'contra_account': m.membership_type.contra_account_currentperiod,
                    'amount': price_thisperiod,
                    'text': _('{full_name} {start} - {end}').format(
                        full_name=self.member.get_full_name(),
                        start=m.start_date.strftime('%d.%m.%Y'),
                        end=date(year=m.start_date.year, month=12, day=31).strftime('%d.%m.%Y'),
                        membership_type=m.membership_type.name)
                        }
                    )
                # add position for next period
                membership_list.append({
                    'contra_account': m.membership_type.contra_account_nextperiod,
                    'amount': price_nextperiod,
                    'text': _('{full_name} {start} - {end}').format(
                        full_name=self.member.get_full_name(),
                        start=date(year=end_date.year, month=1, day=1).strftime('%d.%m.%Y'),
                        end=end_date.strftime('%d.%m.%Y'),
                        membership_type=m.membership_type.name)
                        }
                    )
            else:
                membership_list.append({
                    'contra_account': m.membership_type.contra_account_thisperiod,
                    'amount': m.price(),
                    'text': _('{full_name} {start} - {end} ({membership_type})').format(
                        full_name=self.member.get_full_name(),
                        start=m.start_date.strftime('%d.%m.%Y'),
                        end=end_date.strftime('%d.%m.%Y'),
                        membership_type=m.membership_type.name)
                        }
                    )
        positions.extend(membership_list)

        return positions


class MachinesUsed(models.Model):
    """machines used in Fablog"""

    fablog = models.ForeignKey(
        Fablog,
        on_delete=models.SET_NULL,
        null=True)

    machine = models.ForeignKey(
        "machines.Machine",
        on_delete=models.SET_NULL,
        null=True)

    start_time = models.DateTimeField(
        verbose_name=_("start time"),
        help_text=pgettext_lazy(
            "Machines used",
            "Machine use start time"))

    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("end time"),
        help_text=pgettext_lazy(
            "Machines used",
            "Machine use end time"))

    class Meta:
        verbose_name = _('machine used')
        verbose_name_plural = _('machines used')

    def __str__(self):
        return str(self.machine.name)

    def duration(self):
        if self.end_time and self.start_time:
            duration = self.end_time - self.start_time
        elif self.start_time:
            duration = timezone.now() - self.start_time
        else:
            duration = timedelta()
        return duration
    duration.short_description = _("duration")

    def duration_str(self):
        s = self.duration().seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '%s:%s' % (hours, f'{minutes:02}')

    def units(self):
        return ceil(self.duration() / self.machine.unit)
    units.short_description = _("units")

    def price(self):
        return self.units() * self.machine.price_per_unit
    price.short_description = _("price")

    def clean(self):
        super().clean()
        # end_time should always be after start_time
        if self.end_time:
            if self.end_time < self.start_time:
                raise ValidationError({
                    'end_time': 'End Time must be after start time!'})


class Varia(models.Model):
    """ Various positions for Fablog """
    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("varia name"))
    contra_account = models.ForeignKey(
        "cashier.ContraAccount",
        on_delete=models.PROTECT,
        verbose_name=_("account to"),
        help_text=_("account to bill to"))
    order = models.PositiveSmallIntegerField(
        default=1000,
        verbose_name=_("order"),
        help_text=_("Number to set ordering"))

    class Meta:
        verbose_name = _('varia')
        verbose_name_plural = _('varia')
        ordering = ['order', ]

    def __str__(self):
        return str(self.name)


class FablogVaria(models.Model):
    fablog = models.ForeignKey(
        "Fablog",
        on_delete=models.SET_NULL,
        null=True)
    varia = models.ForeignKey(
        "fablog.Varia",
        on_delete=models.SET_NULL,
        null=True)
    details = models.CharField(
        max_length=255,
        verbose_name=_("details"),
        help_text=_("details"))

    units = models.PositiveSmallIntegerField(
            default=1,
            verbose_name=_("units"),
            help_text=_("Units of Material used"))
    price_per_unit = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("price/unit"),
        help_text=_("price per unit"))

    class Meta:
        verbose_name = _('varia position')
        verbose_name_plural = _('various positions')

    def __str__(self):
        return str(self.varia.name)

    def price(self):
        if self.price_per_unit:
            return self.units * self.price_per_unit
        else:
            return 0
    price.short_description = _("price")

    def booking_text(self):
        text = _('%(varia_name)s: %(details)s') % {
            'varia_name': self.varia.name,
            'details': self.details
            }
        return text


class FablogMemberships(models.Model):
    """ intermediate table linking Fablogs and Memberships"""

    fablog = models.ForeignKey(
        Fablog,
        on_delete=models.SET_NULL,
        null=True)

    membership_type = models.ForeignKey(
        "members.MembershipType",
        on_delete=models.SET_NULL,
        null=True)

    start_date = models.DateField(
        default=date.today,
        verbose_name=_("membership start date"),
        help_text=_("First day of membership"))

    def end_date(self):
        return self.start_date + self.membership_type.duration
    end_date.short_description = _("end date")

    def price(self):
        return self.membership_type.price
    price.short_description = _("price")

    class Meta:
        verbose_name = _('associated Membership')
        verbose_name_plural = _('associated Memberships')

    def __str__(self):
        return str(self.membership_type.name)


class FablogPayments(models.Model):
    """ intermediate table linking Fablogs and Payments"""

    fablog = models.ForeignKey(
        Fablog,
        on_delete=models.SET_NULL,
        null=True)

    payment = models.OneToOneField(
        "cashier.Payment",
        on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('associated Payment')
        verbose_name_plural = _('associated Payments')


class FablogBookings(models.Model):
    """ intermediate table linking Fablogs and Bookings"""

    fablog = models.ForeignKey(
        Fablog,
        on_delete=models.SET_NULL,
        null=True)

    booking = models.OneToOneField(
        "cashier.Booking",
        on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('associated Booking')
        verbose_name_plural = _('associated Bookings')


class FabDay(models.Model):
    """ helper model to facilitate views by date"""

    date = models.DateField(
        verbose_name=_("FabDay"),
        help_text=_("A fabulous day of fabbing at the Fablab"))

    class Meta:
        verbose_name = _('Fabday')
        verbose_name_plural = _('Fabdays')
        ordering = ['-date']

    def __str__(self):
        return _("%(name)s, %(datetime)s") % {
            "name": self._meta.verbose_name,
            "datetime": self.date.strftime('%d.%m.%Y')}
