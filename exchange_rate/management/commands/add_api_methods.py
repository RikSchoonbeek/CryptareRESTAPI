from django.core.management.base import BaseCommand

from exchange_rate.models import ApiMethod, Exchange


class Command(BaseCommand):
    help = "Adds initial api methods to DB, from data defined in dictionary in this management " \
           "command's file."

    def handle(self, *args, **options):
        bitstamp_exchange = Exchange.objects.get(name='Bitstamp')
        bittrex_exchange = Exchange.objects.get(name='Bittrex')
        kraken_exchange = Exchange.objects.get(name='Kraken')
        self.api_method_dict = [
            {
                'short_name': 'Get currencies',
                'url': 'public/getcurrencies',
                'exchange': bittrex_exchange,
            },
            {
                'short_name': 'Get currencies',
                'url': 'public/Assets',
                'exchange': kraken_exchange,
            },
            {
                'short_name': 'Get tradable currency pair info',
                'url': 'trading-pairs-info/',
                'exchange': bitstamp_exchange,
            },
            {
                'short_name': 'Get tradable currency pair info',
                'url': 'public/getmarkets',
                'exchange': bittrex_exchange,
            },
            {
                'short_name': 'Get tradable currency pair info',
                'url': 'public/AssetPairs',
                'exchange': kraken_exchange,
            },
            {
                'short_name': 'Get ticker',
                'url': 'ticker/{currency_pair}/',
                'parameters': 'currency_pair',
                'example': 'ticker/ltcusd/',
                'exchange': bitstamp_exchange,
            },
            {
                'short_name': 'Get ticker',
                'url': 'public/getticker',
                'parameters': 'market',
                'example': 'public/getticker?market=BTC-LTC',
                'exchange': bittrex_exchange,
            },
            {
                'short_name': 'Get ticker',
                'url': 'public/Ticker',
                'parameters': 'pair',
                'example': 'public/Ticker?pair=ZECJPY',
                'exchange': kraken_exchange,
            },
        ]

        for api_method_dict in self.api_method_dict:
            api_method = ApiMethod(
                short_name=api_method_dict['short_name'],
                url=api_method_dict['url'],
                exchange=api_method_dict['exchange'],
            )
            if 'parameters' in api_method_dict:
                setattr(api_method, 'parameters', api_method_dict['parameters'])
            if 'example' in api_method_dict:
                setattr(api_method, 'example', api_method_dict['example'])
            api_method.save()
