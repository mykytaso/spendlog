from django.contrib import admin

from spend_tracker.models import Currency, DefaultCurrency, Unit, Transaction


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(DefaultCurrency)
class DefaultCurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
