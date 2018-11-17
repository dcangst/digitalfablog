# django
from django.forms import ModelForm, Select, BooleanField, ModelChoiceField
from django.utils.translation import gettext_lazy as _

# local
from .models import Payment, PaymentMethod, CashCount


class FablogPaymentForm(ModelForm):

    remainder_as_donation = BooleanField(
        label=_("Add remainder as a donation"),
        help_text=_("Check to automatically add the remainder as a donation"),
        required=False)

    payment_method = ModelChoiceField(
        required=True,
        help_text=_("payment method"),
        widget=Select(attrs={'class': "custom-select"}),
        queryset=PaymentMethod.objects.filter(selectable=True)
        )

    class Meta:
        model = Payment
        fields = ("amount", "payment_method", "remainder_as_donation")


class CashCountForm(ModelForm):

    class Meta:
        model = CashCount
        fields = ("cashier_date", "journal", "total")
        widgets = {
            'journal': Select(attrs={'class': "custom-select"})}

    def __init__(self, *args, **kwargs):
        super(CashCountForm, self).__init__(*args, **kwargs)
        self.fields['journal'].disabled = False
