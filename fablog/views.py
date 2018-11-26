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
from .forms import (NewFablogForm, FablogForm, MachinesUsedInline, FablogMembershipsInline,
                    FablogVariaInline, FablogRefundsInline)
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


class FablogDetailView(LoginRequiredMixin, DetailView):
    model = Fablog
    template_name = "fablog/fablog_detailview.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.closed_at:
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
            FablogMemberships.objects.create(
                fablog=self.object,
                membership_type=membership_type,
                start_date=date.today())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # only get full list of members for labmanagers
        if self.request.user.groups.filter(name="labmanager").exists():
            members_list = User.members.get_members_list()
            context['members_list'] = members_list
        else:
            context['members_list'] = [self.request.user.get_member_list_dict()]
        return context

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()


class FablogUpdateView(PermissionRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    permission_required = 'fablog.change_fablog'

    template_name = "fablog/fablog_updateview.html"
    model = Fablog
    form_class = FablogForm
    # inlines definition moved to get_inlines and get_inline_names

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

    def get_inlines(self):
        if self.request.user.groups.filter(name="labmanager").exists():
            return [MachinesUsedInline, FablogMembershipsInline, FablogVariaInline, FablogRefundsInline]
        else:
            return [MachinesUsedInline, FablogMembershipsInline, FablogVariaInline]

    def get_inlines_names(self):
        if self.request.user.groups.filter(name="labmanager").exists():
            return ['machinesFS', "membershipsFS", "variaFS", "refundsFS"]
        else:
            return ['machinesFS', "membershipsFS", "variaFS"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # only get full list of members for labmanagers
        if self.request.user.groups.filter(name="labmanager").exists():
            members_list = User.members.get_members_list()
            context['members_list'] = members_list
        else:
            context['members_list'] = [self.request.user.get_member_list_dict()]
        return context

    def get_success_url(self):
        return reverse('fablog:home')

    def get_close_url(self):
        return reverse('fablog:transaction', args=(self.get_object().id,))

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """
        self.object = form.save()
        for formset in inlines:
            formset.save()
