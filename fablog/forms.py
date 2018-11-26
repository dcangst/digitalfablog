# django
from django.forms import ModelForm, ModelChoiceField, Select, BaseInlineFormSet, DateTimeField
from django.utils.translation import gettext_lazy as _

# additional
from extra_views import InlineFormSetFactory

# local
from .models import Fablog, MachinesUsed, FablogMemberships, FablogVaria
from members.models import User


class FablogForm(ModelForm):
    created_at = DateTimeField(disabled=True)

    class Meta:
        model = Fablog
        fields = ("created_at", "member", "notes")


class NewFablogForm(ModelForm):
    member = ModelChoiceField(
        widget=Select(attrs={'class': "custom-select"}),
        queryset=User.members.all())

    class Meta:
        model = Fablog
        fields = ("created_at", "member", )


class FablogMachinesUsedInlineFormset(BaseInlineFormSet):

    def close_check(self, valid):
        form_valid = True
        for i in range(0, self.total_form_count()):
            data = self.forms[i].cleaned_data
            if data.get("start_time") and not data.get("end_time"):
                self.forms[i].add_error("end_time", _("Need an end time to close Fablog!"))
                form_valid = False
        return form_valid


class FablogMembershipInlineFormset(BaseInlineFormSet):

    def close_check(self, valid):
        if not valid:
            form_valid = True
            for i in range(0, self.total_form_count()):
                data = self.forms[i].cleaned_data
                if not data.get("membership_type"):
                    form_valid = False
                    self.forms[0].add_error(None, _('You must add a membership!'))
            return form_valid
        else:
            return True


class FablogInlineFormset(BaseInlineFormSet):

    def close_check(self, valid):
        return True


class MachinesUsedInline(InlineFormSetFactory):
    model = MachinesUsed
    formset_class = FablogMachinesUsedInlineFormset
    factory_kwargs = {
        'extra': 1,
        'fields': ("machine", "start_time", "end_time"),
        'widgets': {'machine': Select(attrs={'class': "custom-select"})}}


class FablogVariaInline(InlineFormSetFactory):
    model = FablogVaria
    formset_class = FablogInlineFormset
    factory_kwargs = {
        'extra': 1,
        'fields': '__all__',
        'widgets': {'varia': Select(attrs={'class': "custom-select"})}
    }


class FablogMembershipsInline(InlineFormSetFactory):
    model = FablogMemberships
    formset_class = FablogMembershipInlineFormset
    factory_kwargs = {
        'extra': 1,
        'max_num': 1,
        'fields': '__all__',
        'widgets': {'membership_type': Select(attrs={'class': "custom-select"})}
    }
