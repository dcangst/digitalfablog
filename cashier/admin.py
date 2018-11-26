# Django
from django.contrib import admin

# local
from .models import CashCount, FinancialAccount, Transaction, TransactionMethod, Entry


class EntryInline(admin.TabularInline):
    model = Entry
    fk_name = 'account'
    extra = 1


class CashCountInline(admin.TabularInline):
    model = CashCount
    readonly_fields = ("total", )
    extra = 1


class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'description', 'account_type')
    inlines = (EntryInline, CashCountInline)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "transaction_method", "amount")


admin.site.register(CashCount)
admin.site.register(FinancialAccount, FinancialAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionMethod)
admin.site.register(Entry)
