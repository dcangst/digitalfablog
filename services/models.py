# standard library
from datetime import timedelta

# django
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """ Services """
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"))
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("price"),
        help_text=_("price of service"))

    def __str__(self):
        return self.name
