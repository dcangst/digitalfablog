# django
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.forms.formsets import all_valid
from django.shortcuts import redirect

# additional
from extra_views import UpdateWithInlinesView, NamedFormsetsMixin

# local
from .models import Fablog
from .forms import NewFablogForm, FablogForm, MachinesUsedInline, MaterialsUsedInline, ServicesUsedInline


class Home(LoginRequiredMixin, ListView):
    login_url = "/login/"
    redirect_field_name = 'next'
    template_name = "home.html"
    model = Fablog
    context_object_name = 'fablogs'


class FablogDetailView(DetailView):
    model = Fablog
    template_name = "fablog/fablog_detailview.html"


class FablogCreateView(CreateView):
    template_name = "fablog/fablog_createview.html"
    model = Fablog
    form_class = NewFablogForm

    def get_success_url(self):
        return reverse('fablog:home')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class FablogUpdateView(NamedFormsetsMixin, UpdateWithInlinesView):
    template_name = "fablog/fablog_updateview.html"
    model = Fablog
    form_class = FablogForm
    inlines = [MachinesUsedInline, MaterialsUsedInline, ServicesUsedInline]
    inlines_names = ['machinesFS', 'materialsFS', "servicesFS"]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.closed_at:
            return redirect('fablog:detail', **kwargs)
        return super(UpdateWithInlinesView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # form validation
        self.object = self.get_object()
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
                    if not formset.close_check():
                        inlines_check = False
                if not inlines_check:
                    return self.render_to_response(self.get_context_data(form=form, inlines=inlines))
                else:
                    return HttpResponseRedirect(self.get_close_url())
        else:
            return self.forms_invalid(form, inlines)

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
