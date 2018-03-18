# django
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid
from django.shortcuts import redirect
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

# additional
from extra_views import UpdateWithInlinesView, NamedFormsetsMixin

# local
from .models import Fablog, FablogMemberships
from memberships.models import Membership
from .forms import NewFablogForm, FablogForm, MachinesUsedInline, MaterialsUsedInline, FablogMembershipsInline
from members.models import User


class Home(LoginRequiredMixin, ListView):
    model = Fablog
    context_object_name = 'fablogs'
    template_name = "home.html"

    def get_queryset(self):
        queryset = super(Home, self).get_queryset()
        if not self.request.user.has_perm('fablog.add_fablog'):
            queryset = queryset.filter(member=self.request.user)
        return queryset


class FablogDetailView(LoginRequiredMixin, DetailView):
    model = Fablog
    template_name = "fablog/fablog_detailview.html"


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
        self.object.save()
        if not self.object.member.membership_valid():
            # add membership to fablog
            membership = Membership.objects.get(membership_type=0)
            FablogMemberships.objects.create(fablog=self.object, membership=membership)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = User.members.all()
        members_list = []
        for m in members:
            if m.has_payed:
                status_class = "text-sucess"
                status = "expires " + date_format(m.end_date)
            else:
                status_class = "text-danger"
                if m.end_date:
                    status = "expired " + date_format(m.end_date)
                else:
                    status = _("new")
            members_list.append({
                'pk': m.pk,
                'label': m.get_full_name(),
                'status': status,
                'status_class': status_class})
        context['members_list'] = members_list
        return context


class FablogUpdateView(PermissionRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    permission_required = 'fablog.change_fablog'

    template_name = "fablog/fablog_updateview.html"
    model = Fablog
    form_class = FablogForm
    inlines = [MachinesUsedInline, MaterialsUsedInline, FablogMembershipsInline]
    inlines_names = ['machinesFS', 'materialsFS', "membershipsFS"]

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
        members = User.members.all()
        members_list = []
        for m in members:
            if m.has_payed:
                status_class = "text-sucess"
                status = "expires " + date_format(m.end_date)
            else:
                status_class = "text-danger"
                if m.end_date:
                    status = "expired " + date_format(m.end_date)
                else:
                    status = _("new")
            members_list.append({
                'pk': m.pk,
                'label': m.get_full_name(),
                'status': status,
                'status_class': status_class})
        context['members_list'] = members_list
        return context

    def get_success_url(self):
        return reverse('fablog:home')

    def get_close_url(self):
        return reverse('fablog:booking', args=(self.get_object().id,))

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """
        self.object = form.save()
        for formset in inlines:
            formset.save()
