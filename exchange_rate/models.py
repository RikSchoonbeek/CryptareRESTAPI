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


class Code(models.Model):
    code = models.CharField(max_length=10)
    currency = models.ForeignKey(Currency,
                                 on_delete=models.CASCADE)
    exchange = models.ManyToManyField('Exchange')

    def __str__(self):
        return self.code


class Exchange(models.Model):
    name = models.CharField(max_length=150)
    website = models.URLField()
    api_url = models.URLField()

    def __str__(self):
        return self.name


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
