# django
from django.forms import ModelForm, SplitDateTimeField, Select, BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

# additional
from extra_views import InlineFormSet

# local
from .models import Fablog, MachinesUsed, MaterialsUsed, ServicesUsed


class FablogForm(ModelForm):

    class Meta:
        model = Fablog
        fields = ("created_at", "member", "notes")


class NewFablogForm(ModelForm):

    class Meta:
        model = Fablog
        fields = ("created_at", "member", )
        field_classes = {
            'created_at': SplitDateTimeField,
        }


class FablogMachinesUsedInlineFormset(BaseInlineFormSet):

    def close_check(self):
        valid = True
        for i in range(0, self.total_form_count()):
            data = self.forms[i].cleaned_data
            if data.get("start_time") and not data.get("end_time"):
                self.forms[i].add_error("end_time", _("Need an end time to close Fablog!"))
                valid = False
        return valid


class FablogInlineFormset(BaseInlineFormSet):

    def close_check(self):
        return True


class MachinesUsedInline(InlineFormSet):
    model = MachinesUsed
    formset_class = FablogMachinesUsedInlineFormset
    extra = 1
    fields = ("machine", "start_time", "end_time")
    widgets = {'machine': Select(attrs={'class': "custom-select"})}


class MaterialsUsedInline(InlineFormSet):
    model = MaterialsUsed
    formset_class = FablogInlineFormset
    extra = 1
    fields = '__all__'
    widgets = {'material': Select(attrs={'class': "custom-select"})}


class ServicesUsedInline(InlineFormSet):
    model = ServicesUsed
    formset_class = FablogInlineFormset
    extra = 1
    fields = '__all__'
    widgets = {'service': Select(attrs={'class': "custom-select"})}
