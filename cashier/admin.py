# Django
from django.contrib import admin

# local
from .models import CashCount, CashCountNominals, CashNominal, Currency, \
    FinancialAccount, BookingType, PaymentMethod, Booking


class CashCountNominalsInline(admin.TabularInline):
    model = CashCountNominals
    extra = 1


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1


class CashCountInline(admin.TabularInline):
    model = CashCount
    extra = 1


class CashCountAdmin(admin.ModelAdmin):
    inlines = (CashCountNominalsInline, )
    readonly_fields = ("total", )


class FinancialAccountAdmin(admin.ModelAdmin):
    inlines = (BookingInline, CashCountInline)


admin.site.register(Currency)
admin.site.register(CashNominal)
admin.site.register(CashCount, CashCountAdmin)
admin.site.register(CashCountNominals)
admin.site.register(FinancialAccount, FinancialAccountAdmin)
admin.site.register(PaymentMethod)
admin.site.register(Booking)
admin.site.register(BookingType)
