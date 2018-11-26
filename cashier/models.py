# django
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import pgettext


class FinancialAccount(models.Model):
    """An object representing a financial Account"""
    number = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name=_('journal account number'),
        help_text=_('Account number associated with this journal'))
    name = models.CharField(
        max_length=255,
        verbose_name=_('journal name'),
        help_text=_('Name of the journal'))
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=pgettext(
            "Cashier",
            "description of usage of account (keep it short)"))

    REVENUES = 0      # Ertrag
    EXPENSES = 1      # Aufwand
    ASSETS = 3        # Aktive
    LIABILITIES = 4   # Passive (for completeness sake)
    ACCOUNT_TYPE_CHOICES = (
        (REVENUES, _('Revenues')),
        (EXPENSES, _('Expenses')),
        (ASSETS, _('Assets')),
        (LIABILITIES, _('Liabilities'))
    )

    account_type = models.PositiveSmallIntegerField(
        choices=ACCOUNT_TYPE_CHOICES,
        default=0,
        verbose_name=_('account type'),
        help_text=pgettext(
            'Cashier',
            'type of account'))

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        ordering = ['number', ]

    def __str__(self):
        name = _('%(number)s %(name)s') % {
            'number': self.number,
            'name': self.name}
        return name


class Entry(models.Model):
    """ An entry to an account """
    INCOME = 0
    EXPENSE = 1
    COUNT = 2
    ENTRY_TYPE_CHOICES = (
        (INCOME, _('Income')),
        (EXPENSE, _('Expense')),
        (COUNT, _('Count'))
    )

    entry_type = models.PositiveSmallIntegerField(
        choices=ENTRY_TYPE_CHOICES,
        default=0,
        verbose_name=_('entry type'),
        help_text=pgettext(
            'Cashier',
            'type of entry'))

    account = models.ForeignKey(
        'FinancialAccount',
        related_name='account',
        on_delete=models.PROTECT,
        verbose_name=_('account'),
        help_text=pgettext(
            'Cashier',
            'account for entry'))

    contra_account = models.ForeignKey(
        'FinancialAccount',
        related_name='contraaccount',
        on_delete=models.PROTECT,
        verbose_name=_("contra account"),
        help_text=_("contra account for entry"))

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date & Time'),
        help_text=pgettext(
            'Cashier',
            'Entry date and time'))

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('amount'),
        help_text=_('Amount of the entry'))

    balance = models.DecimalField(
        null=True,
        blank=True,
        max_digits=20,
        decimal_places=2,
        verbose_name=_('current balance'),
        help_text=_('current balance (counted)'))

    text = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name=_('entry text'),
        help_text=pgettext(
            'Cashier',
            'Text of Entry')
        )

    class Meta:
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')
        ordering = ['-timestamp', ]
        permissions = (
            ('view_entries', _('Can view entries')),)

    def __str__(self):
        name = _('%(datetime)s | %(type)s | %(account)s - %(contra_account)s:  %(amount)s ') % {
            'type': self.get_booking_type_display(),
            'datetime': self.timestamp.strftime('%d.%m.%Y %H:%M'),
            'account': self.account.number,
            'contra_account': self.contra_account.number,
            'amount': self.amount
            }
        return name


class Transaction(models.Model):
    """
    A Transaction for a fablog
    this is to seperate payments/expenses from bookings to accounts to allow for partial payment
    """
    transaction_method = models.ForeignKey(
        'TransactionMethod',
        related_name='transactions',
        on_delete=models.PROTECT,
        verbose_name=_('transaction method'),
        help_text=pgettext(
            'Cashier',
            'transaction method'))
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('amount'),
        help_text=_('Amount of the transaction'))
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date & Time'),
        help_text=pgettext(
            'Cashier',
            'Transaction date and time'))

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-amount', ]

    def __str__(self):
        name = _('%(datetime)s | %(method)s ') % {
            'datetime': self.timestamp.strftime('%d.%m.%Y, %H:%M'),
            'method': self.transaction_method.long_name}
        return name


class TransactionMethod(models.Model):
    '''table for storing different available payment types'''
    short_name = models.CharField(
        max_length=3,
        verbose_name=_('short name'),
        help_text=pgettext(
            'payment method',
            'Three letter short name for display.')
        )
    long_name = models.CharField(
        max_length=50,
        verbose_name=_('long name'),
        help_text=pgettext(
            'payment method',
            'Long name of payment method')
        )
    selectable = models.BooleanField(
        default=True,
        verbose_name=_('Selectable'),
        help_text=pgettext(
            'payment method',
            'Used to restrict Select Widgets in Forms'))

    # if the transaction amount is > 0 this is the debit account (de: Soll), otherwise it's credit (de: Haben)
    # the contra account is defined by the associated fablog.
    account = models.ForeignKey(
        FinancialAccount,
        related_name='transaction_methods',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Entry to account'),
        help_text=pgettext(
            'Cashier',
            'Journal for this payment method'))

    class Meta:
        verbose_name = _('transaction method')
        verbose_name_plural = _('transaction methods')
        permissions = (
            ('view_transaction_methods', _('Can view transaction methods')),)

    def __str__(self):
        name = _('%(short_name)s (%(long_name)s)') % {
            'short_name': self.short_name,
            'long_name': self.long_name}
        return name


class CashCount(models.Model):
    """
    A cash count of a journal.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cash_counts',
        on_delete=models.PROTECT,
        verbose_name=_('created by'),
        help_text=pgettext(
            'CashCount',
            'Labmanager who created the cash count'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
        help_text=pgettext(
            'CashCount',
            'Creation date and time'))
    cashier_date = models.DateField(
        verbose_name=_('cash count date'),
        help_text=pgettext(
            'CashCount',
            'Cash count date'))
    fabday = models.ForeignKey(
        'fablog.FabDay',
        related_name='cashcount',
        verbose_name=_('fabday'),
        on_delete=models.PROTECT,
        help_text=pgettext(
            'Cashier',
            'FabDay of this CashCount')
        )

    account = models.ForeignKey(
        'FinancialAccount',
        related_name='cash_counts',
        on_delete=models.PROTECT,
        verbose_name=_('journal'),
        help_text=pgettext(
            'Accounts',
            'Associated journal'))

    total = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('total cash'),
        help_text=_('total cash'))

    entry = models.ForeignKey(
        "cashier.Entry",
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

    def save(self, *args, **kwargs):
        if self.entry:
            # update entry
            self.entry.entry_type = Entry.COUNT,
            self.entry.debit_account = self.account,
            self.entry.credit_account = self.account,
            self.entry.amount = 0,
            self.entry.text = self.__str__()
            self.entry.save()
        else:
            # add entry
            self.entry = Entry.objects.create(
                entry_type=Entry.COUNT,
                account=self.account,
                contra_account=self.account,
                amount=0,
                text=self.__str__())
        super(CashCount, self).save(*args, **kwargs)
