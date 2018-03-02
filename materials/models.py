# django
from django.db import models
from django.utils.translation import gettext_lazy as _


class Material(models.Model):
    """ Materials """
    name = models.CharField(
        max_length=50,
        verbose_name=_("name"),
        help_text=_("name of material"))

    def __str__(self):
        return self.name
