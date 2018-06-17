from django.contrib import admin

from .models import ApiMethod, Code, Currency, Exchange, ExchangeRate, PairApiName, TradablePair


@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'currency', 'get_exchanges')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'type')


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'api_url')


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'bid', 'ask', 'base', 'quote', 'unix_timestamp')

@admin.register(ApiMethod)
class ApiMethodAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'short_name', 'url')

@admin.register(TradablePair)
class TradablePairAdmin(admin.ModelAdmin):
    list_display = ('base', 'quote', 'get_exchange_names', 'get_api_names')

@admin.register(PairApiName)
class PairApiNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_exchanges')
