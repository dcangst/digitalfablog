# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    """A course hosted at fablab"""
    fablogs = models.ManyToManyField(
        "fablog.Fablog",
        related_name="fablogs",
        verbose_name=_("Course Fablogs"))
