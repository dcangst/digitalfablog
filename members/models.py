# base
from datetime import date
from os import path

# django
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify


class Member(models.Model):
    """Temporary Members class"""
    first_name = models.CharField(
        max_length=255,
        verbose_name=_("first name"))
    middle_name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("middle name"))
    last_name = models.CharField(
        max_length=255,
        verbose_name=_("first name"))
    full_name = models.CharField(
        null=True,
        blank=True,
        max_length=510,
        verbose_name=_("full name (automatic)")
        )

    Membership = models.ManyToManyField(
        "cashier.Booking",
        related_name="member",
        through="MembershipBookings",
        verbose_name=_("payments made"))

    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        ordering = ['last_name', 'first_name']

    def save(self, *args, **kwargs):
        if self.middle_name:
            initial = self.middle_name[0].upper()
        else:
            initial = ""

        self.full_name = _("%(first_name)s %(initial)s %(last_name)s") % {
            "first_name": self.first_name,
            "initial": initial,
            "last_name": self.last_name
            }
        super(Member, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name


def legitimation_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    name, ext = path.splitext(filename)
    return 'legitimation_images/{0}_{1}.{2}'.format(
        instance.member.id,
        slugify(instance.member.full_name),
        ext)


class MembershipBookings(models.Model):
    """Intermediate table for Member -> Bookings"""
    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        null=True)
    booking = models.OneToOneField(
        "cashier.Booking",
        on_delete=models.PROTECT,
        null=True)
    start_date = models.DateField(
        default=date(date.today().year, 1, 1),
        verbose_name=_("membership start date"),
        help_text=_("First day of current membership"))
    end_date = models.DateField(
        default=date(date.today().year, 12, 31),
        verbose_name=_("membership start date"),
        help_text=_("First day of current membership"))

    legitimation = models.ImageField(
        upload_to=legitimation_image_path,
        null=True,
        blank=True)

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Membership')
        ordering = ['end_date', ]

    def __str__(self):
        return _("Membership %(year)s") % {
            "year": self.start_date.year}

