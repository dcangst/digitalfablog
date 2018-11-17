# django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# local
from .models import User, Membership
from fablog.models import Fablog


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


class FablogInline(admin.TabularInline):
    model = Fablog
    fk_name = "member"
    extra = 1


class CustomUserAdmin(UserAdmin):
    inlines = (MembershipInline, FablogInline)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name',
                                         'street_and_number', 'zip_code', 'city',
                                         'phone', 'birthday')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',
                       'first_name', 'middle_name', 'last_name',
                       'street_and_number', 'zip_code', 'city',
                       'phone', 'birthday'),
        }),
    )

    # form = UserChangeForm
    # add_form = UserCreationForm
    # change_password_form = AdminPasswordChangeForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    filter_horizontal = ('groups', 'user_permissions',)
    ordering = ['last_name', 'first_name']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Membership)
