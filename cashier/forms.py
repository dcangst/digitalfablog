# django
from django.forms import ModelForm, Select, BooleanField, ModelChoiceField
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# local
from .models import Transaction, TransactionMethod, CashCount


class FablogTransactionForm(ModelForm):

    remainder_as_donation = BooleanField(
        label=_("Add remainder as a donation"),
        help_text=_("Check to automatically add the remainder as a donation"),
        required=False)

    transaction_method = ModelChoiceField(
        required=True,
        help_text=_("transaction method"),
        widget=Select(attrs={'class': "custom-select"}),
        queryset=TransactionMethod.objects.filter(selectable=True))

    class Meta:
        model = Transaction
        fields = ("amount", "transaction_method", "remainder_as_donation")


class CashCountForm(ModelForm):

    class Meta:
        model = CashCount
        fields = ("cashier_date", "account", "total")
        widgets = {
            'account': Select(attrs={'class': "custom-select"})}

    def __init__(self, *args, **kwargs):
        super(CashCountForm, self).__init__(*args, **kwargs)
        self.fields['account'].disabled = False
