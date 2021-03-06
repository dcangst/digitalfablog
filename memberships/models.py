# django
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Membership(models.Model):
    """ Services """
    MEMBERSHIP = 0
    MEMBERSHIP_REDUCED = 1
    TYPE_CHOICES = (
        (MEMBERSHIP, _('Membership')),
        (MEMBERSHIP_REDUCED, _('Membership (Reduced price)')),
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"))
    membership_type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        unique=True,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("price"),
        help_text=_("price of membership"))
    contra_account_currentperiod = models.CharField(
        max_length=4,
        default="3401",
        verbose_name=_("account to"),
        help_text=_("account to bill to"))
    contra_account_nextperiod = models.CharField(
        max_length=4,
        default="2302",
        verbose_name=_("account to"),
        help_text=_("account to bill to"))

    def __str__(self):
        return "{0} ({1})".format(self.name, self.price)
