# Django
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.translation import pgettext as _c


class FinancialAccount(models.Model):
    """An object representing an account"""
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("account name"),
        help_text=_("Name of the account"))
    default_account = models.BooleanField(
        default=False,
        verbose_name=_("default account"),
        help_text=_("Is this the default account for which bookings should be made?"))

    class Meta:
        verbose_name = _('Financial Account')
        verbose_name_plural = _('Financial Accounts')
        permissions = (
            ("view_account", _("Can view account")),)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # check for default account
        if self.default_account:
            if self._meta.model.objects.filter(default_account=True).exclude(id=self.id).exists():
                raise ValidationError(_("Only one account can be the default!"))
        super(FinancialAccount, self).save(*args, **kwargs)
        # create initial booking if necessary
        if not Booking.objects.filter(financial_account=self).exists():
            booking_type, created = BookingType.objects.get_or_create(purpose=2)
            payment_method, created = PaymentMethod.objects.get_or_create(
                short_name="DEF",
                long_name="default payment method",
                selectable=False)
            Booking.objects.create(
                booking_type=booking_type,
                financial_account=self,
                payment_method=payment_method,
                amount=0,
                comment=_("account opening"))


class FinancialAccountBalance(models.Model):
    financial_account = models.ForeignKey(
        "FinancialAccount",
        related_name="balances",
        on_delete=models.PROTECT,
        verbose_name=_("account"),
        help_text=_c(
            "Cashier",
            "Associated account"))
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_("balance"),
        help_text=_("Balance"))

    class Meta:
        verbose_name = _('Account Balance')
        verbose_name_plural = _('Account Balances')
        permissions = (
            ("view_account_balance", _("Can view account balances")),)

    def __str__(self):
        name = _("%(acc_name)s %(name)s %(id)s") % {
            "acc_name": self.financial_account.name,
            "name": self._meta.verbose_name,
            "id": self.id}
        return name


class Booking(models.Model):
    """ A booking to an account """
    booking_type = models.ForeignKey(
        "BookingType",
        related_name="bookings",
        on_delete=models.PROTECT,
        verbose_name=_("booking type"),
        help_text=_c(
            "Cashier",
            "Type of booking"))
    financial_account = models.ForeignKey(
        "FinancialAccount",
        related_name="bookings",
        on_delete=models.PROTECT,
        verbose_name=_("account"),
        help_text=_c(
            "Cashier",
            "Associated account"))
    payment_method = models.ForeignKey(
        "PaymentMethod",
        related_name="bookings",
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
        settings.AUTH_USER_MODEL,
        related_name="bookings_payed_byto",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Payed by/to"),
        help_text=_c(
            "Cashier",
            "User who payed/got payed"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="bookings_created_by",
        blank=True,
        null=True,
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
    comment = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("comment"),
        help_text=_c(
            "Cashier",
            "Comment on Booking")
        )

    balance = models.ForeignKey(
        FinancialAccountBalance,
        related_name="booking_balance",
        on_delete=models.PROTECT,
        verbose_name=_("Balance"),
        help_text=_c(
            "Cashier",
            "Balance after booking"))

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ["-timestamp", ]
        permissions = (
            ("view_bookings", _("Can view bookings")),)

    def __str__(self):
        name = _("%(name)s | %(datetime)s") % {
            "name": self.booking_type.__str__(),
            "datetime": self.timestamp.strftime('%d.%m.%Y %H:%M')}
        return name

    def save(self, *args, **kwargs):
        if FinancialAccountBalance.objects.filter(financial_account=self.financial_account).exists():
            last_bal = FinancialAccountBalance.objects.filter(
                financial_account=self.financial_account).order_by('id').last().balance
        else:
            last_bal = 0
        new_balance = FinancialAccountBalance.objects.create(
            financial_account=self.financial_account,
            balance=last_bal + self.amount)
        self.balance = new_balance
        super(Booking, self).save(*args, **kwargs)


class BookingType(models.Model):
    """Types of bookings"""
    FABLOG = 0
    DONATION = 1
    STORE = 2
    EXPENSES = 3
    CORRECTION = 4
    MEMBERSHIP = 5
    PURPOSE_CHOICES = (
        (FABLOG, _('Fablog')),
        (DONATION, _('Donation')),
        (STORE, _('Store')),
        (EXPENSES, _('Expenses')),
        (CORRECTION, _('Correction')),
        (MEMBERSHIP, _('Membership'))
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
        help_text=_c(
            "booking type",
            "Description of Booking Type")
        )

    class Meta:
        verbose_name = _('booking type')
        verbose_name_plural = _('booking types')
        permissions = (
            ("view_account", _("Can view booking types")),)

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
    selectable = models.BooleanField(
        default=True,
        verbose_name=_("Selectable"),
        help_text=_c(
            "payment method",
            "Used to restrict Select Widgets in Forms"))
    to_account = models.ForeignKey(
        FinancialAccount,
        related_name="payment_methods",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Booking to account"),
        help_text=_c(
            "Cashier",
            "Account for this payment method"))

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        permissions = (
            ("view_payment_methods", _("Can view payment methods")),)

    def __str__(self):
        return self.short_name


class CashCount(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="cash_counts",
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
        related_name="cash_counts",
        on_delete=models.PROTECT,
        verbose_name=_("account"),
        help_text=_c(
            "Accounts",
            "Associated account"))

    cash = models.ManyToManyField(
        "CashNominal",
        through="CashCountNominal",
        verbose_name=_("Cash"))
    currency = models.ForeignKey(
        "Currency",
        related_name="cash_counts",
        on_delete=models.PROTECT,
        verbose_name=_("currency"),
        help_text=_c(
            "Accounts",
            "Currency of cash count"))

    class Meta:
        verbose_name = _('cash count')
        verbose_name_plural = _('cash counts')
        ordering = ['-cashier_date', '-created_at']
        permissions = (
            ("view_cash_counts", _("Can view cash counts")),)

    def __str__(self):
        name = _("%(name)s %(date)s") % {
            "name": self._meta.verbose_name,
            "date": self.cashier_date.strftime("%d.%m.%Y")}
        return name

    def total(self):
        pass


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
    default_currency = models.BooleanField(
        default=False,
        verbose_name=_("default currency"),
        help_text=_("Is this the default currency?"))

    class Meta:
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')
        permissions = (("view_currencies", _("Can view currencies")),)

    def __str__(self):
        return "{0}: {1}/{2}".format(self.abbreviation, self.name, self.fractional_name)

    def save(self, *args, **kwargs):
        # check for default account
        if self.default_currency:
            if self._meta.model.objects.filter(default_currency=True).exclude(id=self.id).exists():
                raise ValidationError(_("Only one curreny can be the default!"))
        super(Currency, self).save(*args, **kwargs)


class CashNominal(models.Model):
    """Cash Nominals"""
    value = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_("value"),
        help_text=_("Value of denomination"))
    currency = models.ForeignKey(
        Currency,
        related_name="nominals",
        on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Cash nominal')
        verbose_name_plural = _('Cash nominals')
        unique_together = (("value", "currency"),)
        ordering = ["value"]
        permissions = (("view_cash_nominals", _("Can view cash nominals")),)

    def __str__(self):
        if self.value < 1:
            return "{0} {1}".format(int(self.value*100), self.currency.fractional_name)
        else:
            return "{0} {1}".format(int(self.value), self.currency.name)


class CashCountNominal(models.Model):
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

    class Meta:
        verbose_name = _('Cash count nominal')
        verbose_name_plural = _('Cash count nominals')
        permissions = (("view_cash_count_nominals", _("Can view cash count nominals")),)
