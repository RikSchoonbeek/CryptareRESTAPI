from django.contrib import admin

from .models import Code, Currency, Exchange, ExchangeRate


admin.site.register([Code,
                     Currency,
                     Exchange,
                     ExchangeRate,
                     ])
