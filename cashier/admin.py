# Django
from django.contrib import admin

# local
from .models import CashCount, Journal, Payment, PaymentMethod, Booking, JournalBalance


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1


class CashCountInline(admin.TabularInline):
    model = CashCount
    readonly_fields = ("total", )
    extra = 1


class JournalAdmin(admin.ModelAdmin):
    inlines = (BookingInline, CashCountInline)


admin.site.register(CashCount)
admin.site.register(Journal, JournalAdmin)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(Booking)
admin.site.register(JournalBalance)
