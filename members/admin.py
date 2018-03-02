from django.contrib import admin
from .models import Member, MembershipBookings
from cashier.models import Booking


class MembershipBookingInline(admin.TabularInline):
    model = MembershipBookings
    extra = 1


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    inlines = (MembershipBookingInline, BookingInline)


admin.site.register(Member, MemberAdmin)
admin.site.register(MembershipBookings)
