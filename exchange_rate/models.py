from django.db import models


class Currency(models.Model):
    CRYPTOCURRENCY = "C"
    FIAT_CURRENCY = "F"
    CURRENCY_TYPE_CHOICES = (
        (CRYPTOCURRENCY, "Crypto"),
        (FIAT_CURRENCY, "Fiat"),
    )
    name = models.CharField(max_length=150)
    symbol = models.CharField(max_length=10,
                              blank=True,
                              null=True,
                              )
    type = models.CharField(max_length=1,
                            choices=CURRENCY_TYPE_CHOICES,
                            )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Code(models.Model):
    code = models.CharField(max_length=10)
    currency = models.ForeignKey(Currency,
                                 on_delete=models.CASCADE,
                                 )
    exchange = models.ManyToManyField('Exchange')

    def __str__(self):
        return self.code

    def get_exchanges(self):
        return ", ".join([exchange.name for exchange in self.exchange.all()])

    class Meta:
        ordering = ['code', 'currency']


class Exchange(models.Model):
    name = models.CharField(max_length=150)
    website = models.URLField()
    api_url = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ExchangeRate(models.Model):
    exchange = models.ForeignKey(Exchange,
                                 on_delete=models.CASCADE,
                                 )
    bid = models.DecimalField(max_digits=60,
                              decimal_places=30,
                              )
    ask = models.DecimalField(max_digits=60,
                              decimal_places=30,
                              )
    base = models.ForeignKey(Currency,
                             on_delete=models.CASCADE,
                             related_name="base_set",
                             )
    quote = models.ForeignKey(Currency,
                              on_delete=models.CASCADE,
                              related_name="quote_set",
                              )
    unix_timestamp = models.PositiveIntegerField()


class ApiMethod(models.Model):
    short_name = models.CharField(max_length=100)
    description = models.TextField(max_length=3000,
                                   blank=True,
                                   null=True,
                                   )
    url = models.CharField(max_length=255)
    example = models.CharField(max_length=255,
                               blank=True,
                               null=True,
                               )
    parameters = models.CharField(max_length=255,
                                  blank=True,
                                  null=True,
                                  )
    exchange = models.ForeignKey(Exchange,
                                 on_delete=models.CASCADE,
                                 )
    api_version = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   )

    def __str__(self):
        return self.short_name


class TradablePair(models.Model):
    base = models.ForeignKey(Currency,
                             on_delete=models.CASCADE,
                             related_name='tradablepair_base_set',
                             )
    quote = models.ForeignKey(Currency,
                              on_delete=models.CASCADE,
                              related_name='tradablepair_quote_set',
                              )
    exchanges = models.ManyToManyField(Exchange)
    api_names = models.ManyToManyField('PairApiName')

    def __str__(self):
        return f"{self.base} - {self.quote}"

    def get_exchange_names(self):
        return ", ".join([exchange.name for exchange in self.exchanges.all()])

    def get_api_names(self):
        return ", ".join([api_name.name for api_name in self.api_names.all()])

    class Meta:
        ordering = ['base', 'quote']


class PairApiName(models.Model):
    name = models.CharField(max_length=100)
    exchanges = models.ManyToManyField(Exchange)

    def __str__(self):
        return self.name

    def get_exchanges(self):
        return ", ".join([exchange.name for exchange in self.exchanges.all()])

    class Meta:
        ordering = ['name']
