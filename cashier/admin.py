# Django
from django.contrib import admin

# local
from .models import CashCount, CashCountNominal, CashNominal, Currency, \
    FinancialAccount, BookingType, PaymentMethod, Booking, FinancialAccountBalance


class CashCountNominalInline(admin.TabularInline):
    readonly_fields = ("total", )
    model = CashCountNominal
    extra = 1


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1


class CashCountInline(admin.TabularInline):
    model = CashCount
    readonly_fields = ("total", )
    extra = 1


class CashCountAdmin(admin.ModelAdmin):
    inlines = (CashCountNominalInline, )
    readonly_fields = ("total", "created_at")


class FinancialAccountAdmin(admin.ModelAdmin):
    inlines = (BookingInline, CashCountInline)


admin.site.register(Currency)
admin.site.register(CashNominal)
admin.site.register(CashCount, CashCountAdmin)
admin.site.register(CashCountNominal)
admin.site.register(FinancialAccount, FinancialAccountAdmin)
admin.site.register(PaymentMethod)
admin.site.register(Booking)
admin.site.register(BookingType)
admin.site.register(FinancialAccountBalance)
