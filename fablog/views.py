# base
from datetime import date

# django
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid
from django.shortcuts import redirect

# additional
from extra_views import UpdateWithInlinesView, NamedFormsetsMixin

# local
from .models import Fablog, FablogMemberships, FabDay
from .forms import NewFablogForm, FablogForm, MachinesUsedInline, FablogMembershipsInline
from members.models import User, MembershipType


class Home(LoginRequiredMixin, ListView):
    model = FabDay
    context_object_name = 'fabdays'
    template_name = "home.html"
    paginate_by = 3

    def get_queryset(self):
        # if no fabday for today has been generated, make one
        FabDay.objects.get_or_create(date=date.today())
        queryset = super(Home, self).get_queryset()
        if not self.request.user.has_perm('fablog.add_fablog'):
            queryset = queryset.filter(fablogs__member=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # included_fablogs_dates = [i['created_at'].date() for i in context['fablogs'].values("created_at")]
        # context["cashcounts"] = CashCount.objects.filter(
        #     cashier_date__in=included_fablogs_dates).distinct('cashier_date')
        return context


class FablogDetailView(LoginRequiredMixin, DetailView):
    model = Fablog
    template_name = "fablog/fablog_detailview.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.closed_at and request.user.has_perm('fablog.add_fablog'):
            return redirect('fablog:update', **kwargs)
        return super(FablogDetailView, self).get(request, *args, **kwargs)


class FablogCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'fablog.add_fablog'

    model = Fablog
    form_class = NewFablogForm
    template_name = "fablog/fablog_createview.html"

    def get_success_url(self):
        return reverse('fablog:home')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.fabday, new = FabDay.objects.get_or_create(date=self.object.created_at)
        self.object.save()
        if not self.object.member.membership_valid():
            # add membership to fablog
            membership_type = MembershipType.objects.get(default_type=True)
            FablogMemberships.objects.create(fablog=self.object, membership_type=membership_type)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members_list = User.members.get_members_list()
        context['members_list'] = members_list
        return context


class FablogUpdateView(PermissionRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    permission_required = 'fablog.change_fablog'

    template_name = "fablog/fablog_updateview.html"
    model = Fablog
    form_class = FablogForm
    inlines = [MachinesUsedInline, FablogMembershipsInline]
    inlines_names = ['machinesFS', "membershipsFS"]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.closed_at:
            return redirect('fablog:detail', **kwargs)
        return super(UpdateWithInlinesView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # form validation
        self.object = self.get_object()
        member_is_valid = self.object.member.membership_valid()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()
        if form.is_valid():
            self.object = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False
        inlines_validated = all_valid(inlines)
        if inlines_validated and form_validated:
            self.forms_valid(form, inlines)
            if "save" in request.POST:
                return HttpResponseRedirect(self.get_success_url())
            else:
                # Perform checks to see if fablog can be closed
                inlines_check = True
                for formset in inlines:
                    if not formset.close_check(member_is_valid):
                        inlines_check = False
                if not inlines_check:
                    return self.render_to_response(self.get_context_data(form=form, inlines=inlines))
                else:
                    return HttpResponseRedirect(self.get_close_url())
        else:
            return self.forms_invalid(form, inlines)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members_list = User.members.get_members_list()
        context['members_list'] = members_list
        return context

    def get_success_url(self):
        return reverse('fablog:home')

    def get_close_url(self):
        return reverse('fablog:payment', args=(self.get_object().id,))

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """
        self.object = form.save()
        for formset in inlines:
            formset.save()
