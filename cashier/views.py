# django
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.apps import apps
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# python
from decimal import Decimal

# local
from .models import Booking
from .forms import FablogBookingForm


class FablogBookingCreateView(CreateView):
    template_name = "fablog/fablog_bookingupdateview.html"
    model = Booking
    form_class = FablogBookingForm

    def get_context_data(self, **kwargs):
        Fablog = apps.get_model("fablog", "Fablog")
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        self.initial = {"amount": fablog.dues}
        context = super().get_context_data(**kwargs)
        context['fablog'] = fablog
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        Fablog = apps.get_model("fablog", "Fablog")
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        form_is_valid = form.is_valid()
        dues = fablog.dues()
        entered_amount = Decimal(request.POST.get("amount"))

        if entered_amount > dues:
            if request.POST.get("remainder_as_donation"):
                self.donation_amount = entered_amount - dues
                self.payment_amount = dues
            else:
                form.add_error(
                    "remainder_as_donation",
                    ValidationError(_('Change Amount or check box to convert remainder to a donation!')))
                form_is_valid = False
        else:
            self.payment_amount = entered_amount
        if form_is_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        Fablog = apps.get_model("fablog", "Fablog")
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        if not self.payment_amount == 0:
            self.object = form.save(commit=False)
            self.object.amount = self.payment_amount
            # add created by
            self.object.created_by = self.request.user
            # add payed_byto
            self.object.payed_byto = fablog.member
            # add booking type
            BookingType = apps.get_model("cashier", "BookingType")
            self.object.booking_type, new = BookingType.objects.get_or_create(purpose=0)
            # add financial account
            FinancialAccount = apps.get_model("cashier", "FinancialAccount")
            self.object.financial_account = FinancialAccount.objects.get(default_account=True)
            # save booking
            self.object.save()
            # add booking to Fablog
            FablogBookings = apps.get_model("fablog", "FablogBookings")
            FablogBookings.objects.create(
                fablog=fablog,
                booking=self.object)
            # add donation if necessary
            if self.donation_amount:
                donation = self.object
                donation.pk = None
                # change amount
                donation.amount = self.donation_amount
                # add created by
                donation.created_by = self.request.user
                # add payed_byto
                donation.payed_byto = fablog.member
                # add booking type
                BookingType = apps.get_model("cashier", "BookingType")
                donation.booking_type, new = BookingType.objects.get_or_create(purpose=1)
                # add financial account
                FinancialAccount = apps.get_model("cashier", "FinancialAccount")
                donation.financial_account = self.object.financial_account
                donation.save()
        # close Fablog if everything has been payed, otherwise make sure its not closed
        if fablog.dues() == 0:
            fablog.closed_by = self.request.user
            fablog.closed_at = timezone.now()
            fablog.save()
        else:
            fablog.closed_by = None
            fablog.closed_at = None
            fablog.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('fablog:home')
