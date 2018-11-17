from django.contrib import admin
from .models import Fablog, MachinesUsed, MaterialsUsed, FablogMemberships, FablogPayments, FablogBookings, FabDay


class MachinesUsedInline(admin.TabularInline):
    readonly_fields = ("start_time", "duration", "units", "price")
    model = MachinesUsed
    extra = 1


class MaterialsUsedInline(admin.TabularInline):
    readonly_fields = ("price", )
    model = MaterialsUsed
    extra = 1


class FablogMembershipsInline(admin.TabularInline):
    readonly_fields = ("price", )
    model = FablogMemberships
    extra = 1


class FablogPaymentsInline(admin.TabularInline):
    model = FablogPayments
    extra = 1


class FablogBookingsInline(admin.TabularInline):
    model = FablogBookings
    extra = 1


class FablogAdmin(admin.ModelAdmin):
    inlines = (MachinesUsedInline, MaterialsUsedInline, FablogMembershipsInline,
               FablogBookingsInline, FablogPaymentsInline)
    readonly_fields = ("total_machines", "total_materials", "total_memberships", "total")


admin.site.register(Fablog, FablogAdmin)
admin.site.register(MachinesUsed)
admin.site.register(FablogMemberships)
admin.site.register(MaterialsUsed)
admin.site.register(FablogBookings)
admin.site.register(FablogPayments)
admin.site.register(FabDay)
