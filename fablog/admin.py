from django.contrib import admin
from .models import (Fablog, MachinesUsed, FablogMemberships, FablogTransactions,
    FablogEntries, FabDay, FablogVaria, Varia)


class MachinesUsedInline(admin.TabularInline):
    readonly_fields = ("start_time", "duration", "units", "amount")
    model = MachinesUsed
    extra = 1


class FablogVariaInline(admin.TabularInline):
    readonly_fields = ("units", "amount")
    model = FablogVaria
    extra = 1


class FablogMembershipsInline(admin.TabularInline):
    readonly_fields = ("amount", )
    model = FablogMemberships
    extra = 1


class FablogTransactionsInline(admin.TabularInline):
    model = FablogTransactions
    extra = 1


class FablogEntriesInline(admin.TabularInline):
    model = FablogEntries
    extra = 1


class FablogAdmin(admin.ModelAdmin):
    inlines = (MachinesUsedInline, FablogVariaInline, FablogMembershipsInline,
               FablogEntriesInline, FablogTransactionsInline)
    readonly_fields = ("total_machines", "total_varia", "total_memberships", "total")


class VariaAdmin(admin.ModelAdmin):
    list_display = ("name", "contra_account", "order")


admin.site.register(Fablog, FablogAdmin)
admin.site.register(MachinesUsed)
admin.site.register(FablogMemberships)
admin.site.register(FablogEntries)
admin.site.register(FablogTransactions)
admin.site.register(FabDay)
admin.site.register(Varia, VariaAdmin)
