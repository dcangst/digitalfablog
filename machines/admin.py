from django.contrib import admin
from .models import Machine, MachineStatus, Status


class MachineStatusInline(admin.TabularInline):
    model = MachineStatus
    extra = 1


class MachineAdmin(admin.ModelAdmin):
    inlines = (MachineStatusInline,)


admin.site.register(Machine, MachineAdmin)
admin.site.register(Status)
