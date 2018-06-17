from django.core.management.base import BaseCommand

from exchange_rate.models import Exchange


class Command(BaseCommand):
    help = "Adds exchange information to DB, from data defined in dictionary in this management" \
           "command's file."

    def handle(self, *args, **options):
        self.exchange_info_dicts = [
            {
                'name': 'Bitstamp',
                'website': 'www.bitstamp.net',
                'api_url': 'https://www.bitstamp.net/api/v2/',
            },
            {
                'name': 'Bittrex',
                'website': 'www.bittrex.com',
                'api_url': 'https://bittrex.com/api/v1.1/',
            },
            {
                'name': 'Kraken',
                'website': 'www.kraken.com',
                'api_url': 'https://api.kraken.com/0/',
            },
        ]

        for exchange_info_dict in self.exchange_info_dicts:
            exchange = Exchange(
                name=exchange_info_dict['name'],
                website=exchange_info_dict['website'],
                api_url=exchange_info_dict['api_url'],
            )
            exchange.save()
