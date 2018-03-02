# Django
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.translation import pgettext as _c


class FinancialAccount(models.Model):
    """An object representing an account"""
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("account name"),
        help_text=_("Name of the account"))
    default_account = models.NullBooleanField(
        default=True,
        unique=True,
        verbose_name=_("default account"),
        help_text=_("Is this the default account for which bookings should be made?"))

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    def __str__(self):
        return self.name


class Booking(models.Model):
    """ A booking to an account """
    booking_type = models.ForeignKey(
        "BookingType",
        on_delete=models.PROTECT,
        verbose_name=_("booking type"),
        help_text=_c(
            "Cashier",
            "Type of booking"))
    financial_account = models.ForeignKey(
        "FinancialAccount",
        on_delete=models.PROTECT,
        verbose_name=_("account"),
        help_text=_c(
            "Cashier",
            "Associated account"))
    payment_method = models.ForeignKey(
        "PaymentMethod",
        on_delete=models.PROTECT,
        verbose_name=_("payment method"),
        help_text=_c(
            "Cashier",
            "payment method"))
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date & Time"),
        help_text=_c(
            "Cashier",
            "Booking date and time"))
    payed_byto = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        verbose_name=_("Payed by/to"),
        help_text=_c(
            "Cashier",
            "User who payed/got payed"))
    created_by = models.ForeignKey(
        User,
        related_name="created_by",
        on_delete=models.PROTECT,
        verbose_name=_("Created by"),
        help_text=_c(
            "Cashier",
            "User who created the booking"))
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("amount"),
        help_text=_("Amount of the booking"))
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("notes"),
        help_text=_c(
            "Cashier",
            "Notes on Booking")
        )

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ["timestamp", ]

    def __str__(self):
        name = _("%(name)s | %(datetime)s") % {
            "name": self.booking_type.__str__(),
            "datetime": self.timestamp.strftime('%d.%m.%Y %H:%M')}
        return name


class BookingType(models.Model):
    """Types of bookings"""
    FABLOG = 0
    DONATION = 1
    STORE = 2
    EXPENSES = 3
    CORRECTION = 4
    PURPOSE_CHOICES = (
        (FABLOG, _('Fablog')),
        (DONATION, _('Donation')),
        (STORE, _('Store')),
        (EXPENSES, _('Expenses')),
        (CORRECTION, _('Correction'))
    )
    purpose = models.PositiveSmallIntegerField(
        choices=PURPOSE_CHOICES,
        unique=True,
        default=0,
    )
    description = models.CharField(
        max_length=250,
        verbose_name=_("description"),
        blank=True,
        null=True,
        help_text=_c(
            "booking type",
            "Description of Booking Type")
        )

    class Meta:
        verbose_name = _('booking type')
        verbose_name_plural = _('booking types')

    def __str__(self):
        return self.PURPOSE_CHOICES[self.purpose][1]


class PaymentMethod(models.Model):
    """table for storing different available payment types"""
    short_name = models.CharField(
        max_length=3,
        verbose_name=_("short name"),
        help_text=_c(
            "payment method",
            "Three letter short name for display.")
        )
    long_name = models.CharField(
        max_length=50,
        verbose_name=_("long name"),
        help_text=_c(
            "payment method",
            "Long name of payment method")
        )

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')

    def __str__(self):
        return self.short_name


class CashCount(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("created by"),
        help_text=_c(
            "Cash",
            "Labmanager who created the cash account"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text=_c(
            "Cash",
            "Creation date and time"))
    cashier_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("cash account date"),
        help_text=_c(
            "Cash",
            "Cash account creation date and time"))

    financial_account = models.ForeignKey(
        "FinancialAccount",
        on_delete=models.PROTECT,
        verbose_name=_("account"),
        help_text=_c(
            "Accounts",
            "Associated account"))

    cash = models.ManyToManyField(
        "CashNominal",
        through="CashCountNominals",
        verbose_name=_("Cash"))

    def total(self):
        pass

    class Meta:
        verbose_name = _('cash count')
        verbose_name_plural = _('cash counts')
        ordering = ['-cashier_date', '-created_at']

    def __str__(self):
        name = _("%(name)s %(date)s") % {
            "name": self._meta.verbose_name,
            "date": self.cashier_date.strftime("%d.%m.%Y")}
        return name


class Currency(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("currency name"),
        help_text=_("Name of currency"))
    fractional_name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("fractional currency name"),
        help_text=_("Name of fractional currency"))
    abbreviation = models.CharField(
        max_length=3,
        unique=True,
        verbose_name=_("currency abbreviation"),
        help_text=_("Abbreviation of currency"))

    class Meta:
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')

    def __str__(self):
        return "{0}: {1}/{2}".format(self.abbreviation, self.name, self.fractional_name)


class CashNominal(models.Model):
    """Cash Nominals"""
    value = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        unique=True,
        verbose_name=_("value"),
        help_text=_("Value of denomination"))
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('nominal')
        verbose_name_plural = _('nominals')
        ordering = ["value"]

    def __str__(self):
        if self.value < 1:
            return "{0} {1}".format(int(self.value*100), self.currency.fractional_name)
        else:
            return "{0} {1}".format(int(self.value), self.currency.name) 


class CashCountNominals(models.Model):
    """Intermediate Table for CashCount -> CashNominal relation"""
    cash_count = models.ForeignKey(
        CashCount,
        on_delete=models.PROTECT,
        null=True)
    cash_nominal = models.ForeignKey(
        CashNominal,
        on_delete=models.PROTECT)
    count = models.PositiveSmallIntegerField(
        verbose_name=_("count"),
        help_text=_("Count of %(nominal)s") % {
            "nominal": cash_nominal.name
        })
