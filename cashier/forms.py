# django
from django.forms import ModelForm, Select, BooleanField, ModelChoiceField
from django.utils.translation import gettext_lazy as _

# additional
from extra_views import InlineFormSet

# local
from .models import Booking, PaymentMethod, CashCount, CashCountNominal, CashNominal


class FablogBookingForm(ModelForm):

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
        model = Booking
        fields = ("amount", "payment_method", "remainder_as_donation")


class CashCountForm(ModelForm):

    class Meta:
        model = CashCount
        fields = ("cashier_date", "financial_account", "currency")
        widgets = {
            'financial_account': Select(attrs={'class': "custom-select"}),
            'currency': Select(attrs={'class': "custom-select"})}

    def __init__(self, *args, **kwargs):
        super(CashCountForm, self).__init__(*args, **kwargs)
        self.fields['financial_account'].disabled = False
        self.fields['currency'].disabled = False


class CashCountNominalInline(InlineFormSet):
    """ use with additional kwarg "currency", a instance of Currency """
    model = CashCountNominal
    can_delete = False
    fields = ("cash_nominal", "count",)
    widgets = {'cash_nominal': Select(attrs={'class': "custom-select"})}

    def get_factory_kwargs(self):
        kwargs = super(InlineFormSet, self).get_factory_kwargs()
        n_cash_nominals = CashNominal.objects.filter(currency=self.kwargs["currency"]).count()
        kwargs.update({
            'extra': n_cash_nominals,
        })
        return kwargs

    def get_initial(self):
        cash_nominals = CashNominal.objects.filter(currency=self.kwargs["currency"])
        self.initial = [{'cash_nominal': x.id, 'count': 0} for x in cash_nominals.all()]
        return self.initial
