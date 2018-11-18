# django
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.translation import pgettext as _c


class Journal(models.Model):
    """An object representing a cashier"""
    number = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name=_('journal account number'),
        help_text=_('Account number associated with this journal'))
    name = models.CharField(
        max_length=255,
        verbose_name=_('journal name'),
        help_text=_('Name of the journal'))

    default_account = models.BooleanField(
        default=False,
        verbose_name=_('default account'),
        help_text=_('Is this the default account for which cash counts should be recorded?'))

    class Meta:
        verbose_name = _('Journal')
        verbose_name_plural = _('Journals')

    def __str__(self):
        name = _('%(number)s %(name)s') % {
            'number': self.number,
            'name': self.name}
        return name

    def clean(self):
        # check for default account
        if self.default_account:
            if self._meta.model.objects.filter(default_account=True).exclude(id=self.id).exists():
                raise ValidationError({'default_account': _('Only one account can be the default!')})


class JournalBalance(models.Model):
    """Helper Model to keep track of account balance"""
    journal = models.ForeignKey(
        'Journal',
        related_name='journals',
        on_delete=models.PROTECT,
        verbose_name=_('journal'),
        help_text=_c(
            'Cashier',
            'Associated journal'))

    balance_expected = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('Balance expected'),
        help_text=_('Balance expected'))

    balance_counted = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Balance true'),
        help_text=_('Balance true'))

    class Meta:
        verbose_name = _('Journal Balance')
        verbose_name_plural = _('Journal Balances')
        permissions = (
            ('view_journal_balance', _('Can view journal balances')),)

    def __str__(self):
        name = _('%(acc_name)s %(id)s: %(true)s (%(expected)s)') % {
            'acc_name': self.journal.__str__(),
            'id': self.id,
            'true': self.balance_counted,
            'expected': self.balance_expected}
        return name


class Booking(models.Model):
    """ A booking to an account """
    BOOKING = 0
    COUNT = 1
    BOOKING_TYPE_CHOICES = (
        (BOOKING, _('Booking')),
        (COUNT, _('Count'))
    )

    booking_type = models.PositiveSmallIntegerField(
        choices=BOOKING_TYPE_CHOICES,
        default=0,
        verbose_name=_('booking type'),
        help_text=_c(
            'Cashier',
            'type of booking'))

    journal = models.ForeignKey(
        'Journal',
        related_name='bookings',
        on_delete=models.PROTECT,
        verbose_name=_('journal'),
        help_text=_c(
            'Cashier',
            'Associated journal'))

    account = models.CharField(
        max_length=4,
        verbose_name=_("account"),
        help_text=_("account to make the booking to/from"))

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date & Time'),
        help_text=_c(
            'Cashier',
            'Booking date and time'))

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('amount'),
        help_text=_('Amount of the booking'))

    comment = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name=_('comment'),
        help_text=_c(
            'Cashier',
            'Comment on Booking')
        )

    balance = models.ForeignKey(
        JournalBalance,
        related_name='booking_balance',
        on_delete=models.PROTECT,
        verbose_name=_('Balance'),
        help_text=_c(
            'Cashier',
            'Balance after booking'))

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-timestamp', ]
        permissions = (
            ('view_bookings', _('Can view bookings')),)

    def __str__(self):
        name = _('%(datetime)s | %(type)s | %(journal)s - %(account)s:  %(amount)s ') % {
            'type': self.get_booking_type_display(),
            'datetime': self.timestamp.strftime('%d.%m.%Y %H:%M'),
            'journal': self.journal.number,
            'account': self.account,
            'amount': self.amount
            }
        return name

    def save(self, *args, **kwargs):
        # get previous balance
        if JournalBalance.objects.filter(journal=self.journal).exists():
            last_balance = JournalBalance.objects.filter(
                journal=self.journal).order_by('id').last()
            last_balance_expected = last_balance.balance_expected
            last_balance_counted = last_balance.balance_counted
        else:
            last_balance_expected = 0
            last_balance_counted = 0

        # add count if cash_count, else add normal booking
        if self.booking_type == self.COUNT:
            new_balance = JournalBalance.objects.create(
                journal=self.journal,
                balance_expected=last_balance_expected + 0,
                balance_counted=self.amount)
            self.amount = 0
        else:
            new_balance = JournalBalance.objects.create(
                journal=self.journal,
                balance_expected=last_balance_expected + self.amount,
                balance_counted=last_balance_counted)
        self.balance = new_balance
        super(Booking, self).save(*args, **kwargs)


class Payment(models.Model):
    """
    A Payment for a fablog
    this is to seperate payments from bookings to accounts to allow for partial payment
    """
    payment_method = models.ForeignKey(
        'PaymentMethod',
        related_name='payments',
        on_delete=models.PROTECT,
        verbose_name=_('payment method'),
        help_text=_c(
            'Cashier',
            'payment method'))
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('amount'),
        help_text=_('Amount of the payment'))
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date & Time'),
        help_text=_c(
            'Cashier',
            'Payment date and time'))

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-amount', ]
        permissions = (
            ('view_bookings', _('Can view bookings')),)

    def __str__(self):
        name = _('%(datetime)s | %(method)s | %(amount)s') % {
            'datetime': self.timestamp.strftime('%d.%m.%Y, %H:%M'),
            'method': self.payment_method.__str__(),
            'amount': self.amount}
        return name

    def clean(self):
        if not self.amount > 0:
            raise ValidationError({'amount': _('Enter an amount larger than zero!')})


class PaymentMethod(models.Model):
    '''table for storing different available payment types'''
    short_name = models.CharField(
        max_length=3,
        verbose_name=_('short name'),
        help_text=_c(
            'payment method',
            'Three letter short name for display.')
        )
    long_name = models.CharField(
        max_length=50,
        verbose_name=_('long name'),
        help_text=_c(
            'payment method',
            'Long name of payment method')
        )
    selectable = models.BooleanField(
        default=True,
        verbose_name=_('Selectable'),
        help_text=_c(
            'payment method',
            'Used to restrict Select Widgets in Forms'))
    journal = models.ForeignKey(
        Journal,
        related_name='payment_methods',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Bookings to journal'),
        help_text=_c(
            'Cashier',
            'Journal for this payment method'))

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        permissions = (
            ('view_payment_methods', _('Can view payment methods')),)

    def __str__(self):
        name = _('%(short_name)s (%(long_name)s)') % {
            'short_name': self.short_name,
            'long_name': self.long_name}
        return name


class CashCount(models.Model):
    """
    A cash count of a journal.

    bookings are generated in post_save signal
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cash_counts',
        on_delete=models.PROTECT,
        verbose_name=_('created by'),
        help_text=_c(
            'Cash',
            'Labmanager who created the cash account'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
        help_text=_c(
            'Cash',
            'Creation date and time'))
    cashier_date = models.DateField(
        default=timezone.now,
        verbose_name=_('cash count date'),
        help_text=_c(
            'Cash',
            'Cash count date'))

    journal = models.ForeignKey(
        'Journal',
        related_name='cash_counts',
        on_delete=models.PROTECT,
        verbose_name=_('journal'),
        help_text=_c(
            'Accounts',
            'Associated journal'))

    fabday = models.ForeignKey(
        'fablog.FabDay',
        related_name='cashcount',
        verbose_name=_('fabday'),
        on_delete=models.PROTECT,
        help_text=_c(
            'Cashier',
            'FabDay of this CashCount')
        )

    total = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('total cash'),
        help_text=_('total cash'))

    booking = models.ForeignKey(
        "cashier.Booking",
        blank=True,
        null=True,
        on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('cash count')
        verbose_name_plural = _('cash counts')
        ordering = ['-cashier_date', '-created_at']
        permissions = (
            ('view_cash_counts', _('Can view cash counts')),)

    def __str__(self):
        name = _('%(name)s %(date)s: %(total)s') % {
            'name': self._meta.verbose_name,
            'date': self.cashier_date.strftime('%d.%m.%Y'),
            'total': self.total}
        return name
