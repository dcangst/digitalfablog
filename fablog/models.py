# standard library
from datetime import timedelta, date
from math import ceil

# Django
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as _c


class Fablog(models.Model):
    """Fablog object"""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_fablogs",
        on_delete=models.PROTECT,
        verbose_name=_("Created by"),
        help_text=_c(
            "Fablog",
            "Labmanager who created the Fablog"))
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("created at"),
        help_text=_c(
            "Fablog",
            "Creation date and time"))

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="closed_fablogs",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Closed by"),
        help_text=_c(
            "Fablog",
            "Labmanager who closed the Fablog"))
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("closed at"),
        help_text=_c(
            "Fablog",
            "Closure date and time"))

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="fablogs",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("member"),
        help_text=_c(
            "Fablog",
            "Member")
        )

    notes = models.TextField(
        blank=True,
        verbose_name=_("notes"),
        help_text=_c(
            "Fablog",
            "Notes on the Fablog")
        )

    machines = models.ManyToManyField(
        "machines.Machine",
        through="MachinesUsed",
        verbose_name=_("machines used"))
    materials = models.ManyToManyField(
        "materials.Material",
        through="MaterialsUsed",
        verbose_name=_("materials used"))
    memberships = models.ManyToManyField(
        "memberships.Membership",
        through="FablogMemberships",
        verbose_name=_("Memberships"))
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

    @property
    def fablog_date(self):
        fablog_date = _("%(day)s.%(month)s.%(year)s") % {
            "day": self.created_at.day,
            "month": self.created_at.month,
            "year": self.created_at.year}
        return fablog_date

    def total_machines(self):
        machines = self.machinesused_set.all()
        total_machine_costs = 0
        for machine in machines:
            total_machine_costs += machine.price()
        return total_machine_costs
    total_machines.short_description = _("subtotal machines")

    def total_materials(self):
        materials = self.materialsused_set.all()
        total_material_costs = 0
        for material in materials:
            total_material_costs += material.price()
        return total_material_costs
    total_materials.short_description = _("subtotal materials")

    def total_memberships(self):
        memberships = self.fablogmemberships_set.all()
        total_membership_costs = 0
        for membership in memberships:
            total_membership_costs += membership.price()
        return total_membership_costs
    total_memberships.short_description = _("subtotal memberships")

    def total_bookings(self):
        payments = self.fablogbookings_set.all()
        total_payments = 0
        for payment in payments:
            total_payments += payment.booking.amount
        return total_payments
    total_bookings.short_description = _("total bookings")

    def total(self):
        return self.total_machines() + self.total_materials() + self.total_memberships()
    total.short_description = _("total overall")

    def dues(self):
        return self.total()-self.total_bookings()
    dues.short_description = _("dues")


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
        help_text=_c(
            "Machines used",
            "Machine use start time"))
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("end time"),
        help_text=_c(
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


class MaterialsUsed(models.Model):
    """materials used in Fablog"""
    fablog = models.ForeignKey(
        Fablog,
        on_delete=models.SET_NULL,
        null=True)
    material = models.ForeignKey(
        "materials.Material",
        on_delete=models.SET_NULL,
        null=True)
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
        verbose_name = _('material used')
        verbose_name_plural = _('materials used')

    def __str__(self):
        return str(self.material.name)

    def price(self):
        if self.price_per_unit:
            return self.units * self.price_per_unit
        else:
            return 0
    price.short_description = _("price")


class FablogMemberships(models.Model):
    fablog = models.ForeignKey(
        Fablog,
        on_delete=models.SET_NULL,
        null=True)
    membership = models.ForeignKey(
        "memberships.Membership",
        on_delete=models.SET_NULL,
        null=True)
    start_date = models.DateField(
        default=date(date.today().year, 1, 1),
        verbose_name=_("membership start date"),
        help_text=_("First day of membership"))
    end_date = models.DateField(
        default=date(date.today().year, 12, 31),
        verbose_name=_("membership end date"),
        help_text=_("Last day of membership"))

    def price(self):
        return self.membership.price

    price.short_description = _("price")

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')

    def __str__(self):
        return str(self.membership.name)


class FablogBookings(models.Model):
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
