# base
from datetime import timedelta

# django
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Machine(models.Model):
    """Machines at the fablab"""
    name = models.TextField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("machine name"))
    abbreviation = models.TextField(
        default="?",
        max_length=5,
        verbose_name=_("Abbreviation"),
        help_text=_("Abbreviation shown in overviews"))
    color = models.TextField(
        max_length=30,
        default="#212529",  # gray 900
        verbose_name=_("Overview color"),
        help_text=_("Color used in Overview. Any CSS syntax will work."))
    unit = models.DurationField(
        default=timedelta(minutes=30),
        verbose_name=_("unit"),
        help_text=_("unit"))
    price_per_unit = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("price/unit"),
        help_text=_("price per unit"))
    status = models.ManyToManyField(
        "Status",
        through="MachineStatus",
        verbose_name=_("machine status"))

    class Meta:
        verbose_name = _('machine')
        verbose_name_plural = _('machines')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_current_status(self):
        # active statuses
        current_status = MachineStatus.objects.current().filter(machine=self)
        if not current_status.exists():
            # set default status
            default_status, _new = Status.objects.get_or_create(name="OK")
            newMachineStatus = MachineStatus(
                machine=self,
                status=default_status,
                start_time=timezone.now())
            newMachineStatus.save()
        return current_status


class MachineStatusManager(models.Manager):
    def current(self):
        """Get the currently active status"""
        return self.filter(
            Q(end_time__gt=timezone.now()) | Q(end_time__isnull=True) & Q(start_time__lte=timezone.now()))


class MachineStatus(models.Model):
    """ List of Statuses for a specific machine (intermediate model)"""
    machine = models.ForeignKey(
        "Machine",
        on_delete=models.SET_NULL,
        null=True)
    status = models.ForeignKey(
        "Status",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Status"))
    start_time = models.DateTimeField(
        verbose_name=_("start time"),
        help_text=_("Machine status start"))
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("end time"),
        help_text=_("Machine status end time"))
    details = models.TextField(
        blank=True,
        verbose_name=_("details"),
        help_text=_("Details concerning the machine status"))
    objects = MachineStatusManager()

    class Meta:
        verbose_name = _("Machine Satus")
        verbose_name_plural = _("Machine Statuses")
        ordering = ["-start_time"]

    def is_current(self):
        if not self.end_time or self.end_time > timezone.now():
            return True
        else:
            return False


class Status(models.Model):
    """ Possible statuses of machines """
    SEVERITY_CHOICES = (
        (0, _('low')),
        (1, _('medium')),
        (2, _('high')),
    )
    severity = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("severity"),
        help_text=_("severity of status"))
    name = models.TextField(
        verbose_name=_("name"))

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')

    def __str__(self):
        verb_name = Status._meta.get_field('severity').verbose_name.title()
        return self.name + " (" + verb_name + ": " + str(self.severity) + ")"
