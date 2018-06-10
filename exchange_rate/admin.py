from django.contrib import admin

from .models import Currency, Exchange, ExchangeRate


admin.site.register([Currency,
                    Exchange,
                    ExchangeRate,]
                    )
