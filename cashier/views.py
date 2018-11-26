# base
from decimal import Decimal

# django
from django.views.generic import CreateView, ListView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.apps import apps
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings

# local
from .models import Transaction, Entry, FinancialAccount, CashCount
from .forms import FablogTransactionForm, CashCountForm
from fablog.models import FabDay


class AccountJournalView(PermissionRequiredMixin, ListView):
    permission_required = 'cashier.can_view_entries'

    template_name = 'cashier/account_journal_view.html'
    context_object_name = 'entries'

    def get_queryset(self):
        self.account = get_object_or_404(FinancialAccount, pk=self.kwargs['pk'])
        # annotate balance expected here
        return Entry.objects.filter(account=self.account)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account'] = self.account
        return context


class FablogTransactionCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'cashier.add_entry'

    template_name = 'fablog/fablog_bookingupdateview.html'
    model = Transaction
    form_class = FablogTransactionForm

    def get_context_data(self, **kwargs):
        Fablog = apps.get_model('fablog', 'Fablog')
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        self.initial = {'amount': fablog.dues()}
        context = super().get_context_data(**kwargs)
        context['fablog'] = fablog
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        Fablog = apps.get_model('fablog', 'Fablog')
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        form_is_valid = form.is_valid()
        dues = fablog.dues()
        entered_amount = Decimal(request.POST.get('amount'))
        if entered_amount > dues:
            if request.POST.get('remainder_as_donation'):
                self.donation_amount = entered_amount - dues
                self.payment_amount = dues
            else:
                form.add_error(
                    'remainder_as_donation',
                    ValidationError(_('Change Amount or check box to convert remainder to a donation!')))
                form_is_valid = False
        else:
            self.payment_amount = entered_amount
            self.donation_amount = None
        if form_is_valid:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        Fablog = apps.get_model('fablog', 'Fablog')
        fablog = Fablog.objects.get(pk=self.kwargs['pk'])
        # add donation to fablog if necessary
        if self.donation_amount:
            Varia = apps.get_model('fablog', 'Varia')
            if not Varia.objects.filter(contra_account__number=settings.DONATION_CONTRA_ACCOUNT_NUMBER).exists():
                # create defaults
                FinancialAccount = apps.get_model('cashier', 'FinancialAccount')
                donation_contra_account, created = FinancialAccount.objects.get_or_create(
                    number=settings.DONATION_CONTRA_ACCOUNT_NUMBER,
                    defaults={
                        'name': 'DEFAULT DONATION ACCOUNT',
                        'account_type': FinancialAccount.REVENUES})
                if created:
                    # IMPLEMENT LOGGING
                    pass
                donation_varia = Varia.objects.create(
                    name='DEFAULT DONATION VARIA',
                    contra_account=donation_contra_account)
            else:
                donation_varia = Varia.objects.filter(
                    contra_account__number=settings.DONATION_CONTRA_ACCOUNT_NUMBER).first()
            FablogVaria = apps.get_model('fablog', 'FablogVaria')
            FablogVaria.objects.create(
                fablog=fablog,
                varia=donation_varia,
                details=fablog.member.get_full_name(),
                units=1,
                price_per_unit=self.donation_amount)
        # add transaction to fablog
        FablogTransactions = apps.get_model('fablog', 'FablogTransactions')
        self.object = form.save()
        FablogTransactions.objects.create(
            fablog=fablog,
            transaction=self.object)
        # update fablog.closed_by == the last labmanager who took a transaction
        fablog.closed_by = self.request.user
        fablog.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('fablog:detail', args=[str(self.kwargs['pk'])])


class CashCountCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'cashier.add_cashcount'

    template_name = 'cashier/cashcount_createview.html'
    model = CashCount
    form_class = CashCountForm

    def get_success_url(self):
        return reverse('fablog:home')

    def get_initial(self):
        account, created = FinancialAccount.objects.get_or_create(
            number=settings.DEFAULT_ACCOUNT_NUMBER,
            defaults={
                "name": "DEFAULT CASH ACCOUNT",
                'account_type': FinancialAccount.REVENUES})
        if created:
            # IMPLEMENT LOGGING
            pass
        self.initial = {'account': account}
        return super(CashCountCreateView, self).get_initial()

    def form_valid(self, form):
        '''
        If the form and formsets are valid, save the associated models.
        '''
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.fabday, new = FabDay.objects.get_or_create(date=self.object.cashier_date)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())
