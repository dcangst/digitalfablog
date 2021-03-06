# base
from datetime import date
from os import path

# django
from django.db import models
from django.db.models import Q, When, Case, Value, Max
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
            self,
            email,
            first_name, last_name,
            street_and_number, zip_code, city,
            phone, birthday,
            password, **extra_fields):

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name, last_name=last_name,
            street_and_number=street_and_number, zip_code=zip_code, city=city,
            phone=phone, birthday=birthday, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self,
            email,
            first_name, last_name,
            street_and_number, zip_code, city,
            phone, birthday,
            password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, first_name, last_name, street_and_number,
                                 zip_code, city, phone, birthday,
                                 password, **extra_fields)

    def create_superuser(
            self,
            email,
            first_name, last_name,
            street_and_number, zip_code, city,
            phone, birthday,
            password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, first_name, last_name, street_and_number,
                                 zip_code, city, phone, birthday,
                                 password, **extra_fields)


class MemberUserManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        today = date.today()
        queryset = queryset.annotate(
            has_payed=Case(
                When(Q(membership__end_date__gte=today), then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()),
            end_date=Max('membership__end_date'))
        return queryset.order_by('-has_payed')

    def get_members_list(self):
        members = self.all()
        members_list = []
        for m in members:
            if m.has_payed:
                status_class = "text-sucess"
                status = _("expires {date}").format(date = date_format(m.end_date))
            else:
                status_class = "text-danger"
                if m.end_date:
                    status = _("expired {date}").format(date = date_format(m.end_date))
                else:
                    status = _("new")
            members_list.append({
                'pk': m.pk,
                'label': m.get_full_name(),
                'status': status,
                'status_class': status_class})
        return(members_list)


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    email = models.EmailField(
        _('email address'),
        unique=True)
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=255)
    middle_name = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_("middle name"))
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=255)
    street_and_number = models.CharField(
        verbose_name=_('Street and number'),
        max_length=255)
    zip_code = models.CharField(
        verbose_name=_('ZIP Code'),
        max_length=255)
    city = models.CharField(
        verbose_name=_('City'),
        max_length=255)
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=255)
    birthday = models.DateField(
        verbose_name=_('Birthday'))

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()
    members = MemberUserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name', 'street_and_number',
                       'zip_code', 'city', 'phone', 'birthday']

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['last_name', 'first_name']
        permissions = (
            ("view_members", _("Can view members")),)

    def __str__(self):
        return self.get_full_name()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        if self.middle_name:
            initial = " {0} ".format(self.middle_name[0].upper())
        else:
            initial = " "

        full_name = _("%(first_name)s%(initial)s%(last_name)s") % {
            "first_name": self.first_name,
            "initial": initial,
            "last_name": self.last_name
            }
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def membership_valid(self):
        if self.membership.exists():
            if self.membership.first().end_date > date.today():
                return True
        return False


def legitimation_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    name, ext = path.splitext(filename)
    return 'legitimation_images/{0}_{1}.{2}'.format(
        instance.member.id,
        slugify(instance.member.get_full_name()),
        ext)


class Membership(models.Model):
    """Intermediate table for User Memberships -> Fablog"""
    member = models.ForeignKey(
        User,
        related_name="membership",
        on_delete=models.PROTECT,
        null=True)
    fablog = models.OneToOneField(
        "fablog.Fablog",
        on_delete=models.PROTECT,
        null=True)
    start_date = models.DateField(
        default=date(date.today().year, 1, 1),
        verbose_name=_("membership start date"),
        help_text=_("First day of membership"))
    end_date = models.DateField(
        default=date(date.today().year, 12, 31),
        verbose_name=_("membership end date"),
        help_text=_("Last day of membership"))

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
