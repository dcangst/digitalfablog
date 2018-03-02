# django
from django.forms import ModelForm, Select, BooleanField
from django.utils.translation import gettext_lazy as _

# local
from .models import Booking


class FablogBookingForm(ModelForm):

    remainder_as_donation = BooleanField(
        label=_("Add remainder as a donation"),
        help_text=_("Check to automatically add the remainder as a donation"),
        required=False)

    class Meta:
        model = Booking
        fields = ("amount", "payment_method", "remainder_as_donation")
        widgets = {'payment_method': Select(attrs={'class': "custom-select"})}
