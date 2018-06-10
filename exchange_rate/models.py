from django.db import models


class Currency(models.Model):
    CRYPTOCURRENCY = "C"
    FIAT_CURRENCY = "F"
    CURRENCY_TYPE_CHOICES = (
        (CRYPTOCURRENCY, "Crypto"),
        (FIAT_CURRENCY, "Fiat"),
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10,
                              blank=True,
                              null=True,
                              )
    type = models.CharField(max_length=1,
                            choices=CURRENCY_TYPE_CHOICES,
                            )

    def __str__(self):
        return self.name


class Exchange(models.Model):
    name = models.CharField(max_length=150)
    website = models.URLField()


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
    datetime = models.DateTimeField()
