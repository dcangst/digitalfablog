from django.contrib import admin
from .models import Fablog, MachinesUsed, MaterialsUsed, ServicesUsed, FablogBookings


class MachinesUsedInline(admin.TabularInline):
    readonly_fields = ("start_time", "duration", "units", "price")
    model = MachinesUsed
    extra = 1


class MaterialsUsedInline(admin.TabularInline):
    readonly_fields = ("price", )
    model = MaterialsUsed
    extra = 1


class ServicesUsedInline(admin.TabularInline):
    readonly_fields = ("price", )
    model = ServicesUsed
    extra = 1


class FablogBookingsInline(admin.TabularInline):
    model = FablogBookings
    extra = 1


class FablogAdmin(admin.ModelAdmin):
    inlines = (MachinesUsedInline, MaterialsUsedInline, ServicesUsedInline, FablogBookingsInline, )
    readonly_fields = ("total_machines", "total_materials", "total_services", "total")


admin.site.register(Fablog, FablogAdmin)
admin.site.register(MachinesUsed)
admin.site.register(ServicesUsed)
admin.site.register(MaterialsUsed)
admin.site.register(FablogBookings)
