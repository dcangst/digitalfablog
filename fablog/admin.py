from django.contrib import admin
from .models import Fablog, MachinesUsed, FablogMemberships, FablogPayments,\
    FablogBookings, FabDay, FablogVaria, Varia, FablogExpenses


class MachinesUsedInline(admin.TabularInline):
    readonly_fields = ("start_time", "duration", "units", "price")
    model = MachinesUsed
    extra = 1


class FablogVariaInline(admin.TabularInline):
    readonly_fields = ("units", "price")
    model = FablogVaria
    extra = 1


class FablogMembershipsInline(admin.TabularInline):
    readonly_fields = ("price", )
    model = FablogMemberships
    extra = 1


class FablogPaymentsInline(admin.TabularInline):
    model = FablogPayments
    extra = 1


class FablogExpensesInline(admin.TabularInline):
    model = FablogExpenses
    extra = 1


class FablogBookingsInline(admin.TabularInline):
    model = FablogBookings
    extra = 1


class FablogAdmin(admin.ModelAdmin):
    inlines = (MachinesUsedInline, FablogVariaInline, FablogMembershipsInline, FablogExpensesInline,
               FablogBookingsInline, FablogPaymentsInline)
    readonly_fields = ("total_machines", "total_varia", "total_memberships", "total")


admin.site.register(Fablog, FablogAdmin)
admin.site.register(MachinesUsed)
admin.site.register(FablogMemberships)
admin.site.register(FablogBookings)
admin.site.register(FablogPayments)
admin.site.register(FabDay)
admin.site.register(Varia)
