# base
from decimal import Decimal

# django
from django.views.generic import CreateView, ListView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.apps import apps
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import PermissionRequiredMixin

# additional
from extra_views import CreateWithInlinesView, NamedFormsetsMixin

# local
from .models import Booking, FinancialAccount, CashCount, Currency
from .forms import FablogBookingForm, CashCountForm, CashCountNominalInline


class AccountBookingListView(PermissionRequiredMixin, ListView):
    permission_required = 'cashier.can_view_bookings'

    template_name = "cashier/accountbooking_listview.html"
    context_object_name = 'bookings'

    def get_queryset(self):
        self.financial_account = get_object_or_404(FinancialAccount, pk=self.kwargs['pk'])
        return Booking.objects.filter(financial_account=self.financial_account)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['financial_account'] = self.financial_account
        return context


class FablogBookingCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'cashier.add_booking'

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
        self.membership_amount = fablog.total_memberships()
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
            if self.membership_amount > entered_amount:
                form.add_error(
                    "amount",
                    ValidationError(_('Membership must be payed in full.')))
                form_is_valid = False
            else:
                self.payment_amount = entered_amount
                self.donation_amount = None
        if form_is_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        Fablog = apps.get_model("fablog", "Fablog")
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        if not self.payment_amount == 0:
            # get common models
            BookingType = apps.get_model("cashier", "BookingType")
            FablogBookings = apps.get_model("fablog", "FablogBookings")

            self.object = form.save(commit=False)
            # add financial account
            if self.object.payment_method.to_account:
                self.object.financial_account = self.object.payment_method.to_account
            else:
                self.object.financial_account = FinancialAccount.objects.get(default_account=True)
            # add created by
            self.object.created_by = self.request.user
            # add payed_byto
            self.object.payed_byto = fablog.member
            # if membership on fablog make two bookings and add Membership to member
            if self.membership_amount > 0:
                # make seperate booking for membership
                payment_amount = self.payment_amount - self.membership_amount
            else:
                payment_amount = self.payment_amount
            self.object.amount = payment_amount
            # add booking type
            self.object.booking_type, new = BookingType.objects.get_or_create(purpose=0)
            # save booking
            self.object.save()
            # add booking to Fablog
            FablogBookings.objects.create(
                fablog=fablog,
                booking=self.object)
            # add donation if necessary
            if self.donation_amount:
                donation = self.object
                donation.pk = None
                # change amount
                donation.amount = self.donation_amount
                # change booking type
                donation.booking_type, new = BookingType.objects.get_or_create(purpose=1)
                donation.save()
            # add membership booking if necessary
            if self.membership_amount > 0:
                membership_booking = self.object
                membership_booking.pk = None
                membership_booking.amount = self.membership_amount
                membership_booking.booking_type, new = BookingType.objects.get_or_create(purpose=5)
                membership_booking.save()
                # add to fablog
                FablogBookings.objects.create(
                    fablog=fablog,
                    booking=membership_booking)
                # add to Member
                Membership = apps.get_model("members", "Membership")
                Membership.objects.create(
                    member=fablog.member,
                    booking=membership_booking,
                    # use first, because only on should be present. (as defined in the modelform)
                    start_date=fablog.fablogmemberships_set.first().start_date,
                    end_date=fablog.fablogmemberships_set.first().end_date)
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


class CashCountCreateView(PermissionRequiredMixin, NamedFormsetsMixin, CreateWithInlinesView):
    permission_required = 'cashier.add_cashcount'

    template_name = "cashier/cashcount_createview.html"
    model = CashCount
    form_class = CashCountForm
    inlines = [CashCountNominalInline, ]
    inlines_names = ['nominalsFS', ]

    def get_success_url(self):
        return reverse('fablog:home')

    def get_initial(self):
        self.currency = Currency.objects.get(default_currency=True)
        self.kwargs.update({"currency": self.currency})
        account = FinancialAccount.objects.get(default_account=True)
        self.initial = {"currency": self.currency, "financial_account": account}
        return super(CashCountCreateView, self).get_initial()
