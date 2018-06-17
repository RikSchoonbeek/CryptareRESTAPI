import json
import requests

from django.core.management.base import BaseCommand

from exchange_rate.models import ApiMethod, Code, Currency, Exchange, PairApiName, TradablePair

from ._utils import correct_currency_name


class Command(BaseCommand):
    help = "Adds exchange information to DB, from data defined in dictionary in this management" \
           "command's file."

    def handle(self, *args, **options):
        exchanges = Exchange.objects.all()
        for exchange in exchanges:
            print(f"\nExchange: {exchange.name}\n")
            api_url = self.get_url(exchange)
            all_pair_data = self.return_pair_data(api_url, exchange.name)
            self.handle_pair_data(all_pair_data, exchange)

    def handle_pair_data(self, all_pair_data, exchange):
        """
        Takes all pair data from an api, handles it further.
        """
        if exchange.name in ('Bitstamp', 'Bittrex'):
            for pair_data in all_pair_data:
                pair_data_dict = self.return_pair_data_dict(pair_data, exchange)
                self.add_pair_to_db(pair_data_dict, exchange)
        else:
            for k, pair_data in all_pair_data.items():
                pair_data_dict = self.return_pair_data_dict(pair_data, exchange)
                self.add_pair_to_db(pair_data_dict, exchange)

    def get_url(self, exchange):
        """
        Takes an exchange object, returns the url needed to get the data from the api.
        """
        base_url = exchange.api_url
        url_end = ApiMethod.objects.get(short_name='Get tradable currency pair info',
                                        exchange=exchange,
                                        ).url
        return base_url + url_end

    def return_pair_data(self, url, exchange_name):
        """
        Takes the url and exchange name, gets calls the function which returns the api data,
        returns the part of the data which contains only the pair data.
        """
        response_dict = self.return_api_data(url)

        if exchange_name == 'Bitstamp':
            return response_dict
        if exchange_name in ('Bittrex', 'Kraken'):
            return response_dict['result']

    def return_api_data(self, url):
        """
        Takes the api url, returns full response data converted to Python format, dict or list.
        """
        response = requests.get(url)
        response_dict = json.loads(response.text)
        return response_dict

    def return_pair_data_dict(self, raw_pair_data, exchange):
        """
        Takes the raw response data for one pair, calls an exchange-specific function on it
        which will make it into a nicely formatted pair_data_dict.

        pair_data_dict format:
        {
        'base': <Currency instance>,
        'quote': <Currency instance>,
        'exchange': <Exchange object to which current data relates>,
        'api_name': <pair name used for api calls, as string>,
        }
        """
        if exchange.name == 'Bitstamp':
            return self.return_bitstamp_pair_data_dict(raw_pair_data, exchange)
        if exchange.name == 'Bittrex':
            return self.return_bittrex_pair_data_dict(raw_pair_data, exchange)
        if exchange.name == 'Kraken':
            return self.return_kraken_pair_data_dict(raw_pair_data, exchange)

    def return_bitstamp_pair_data_dict(self, raw_pair_data, exchange):
        """
        Takes the raw response data for one pair of Bitstamp, calls an exchange-specific
        function on it which will make it into a nicely formatted pair_data_dict.

        pair_data_dict format:
        {
        'base': <Currency instance>,
        'quote': <Currency instance>,
        'exchange': <Exchange object to which current data relates>,
        'api_name': <pair name used for api calls, as string>,
        }
        """
        base_name, quote_name = raw_pair_data['description'].split(' / ')
        base_name = correct_currency_name(base_name)
        quote_name = correct_currency_name(quote_name)
        base_instance = self.get_currency_instance(base_name)
        quote_instance = self.get_currency_instance(quote_name)
        api_name = raw_pair_data['url_symbol']
        return self.form_pair_data_dict(base_instance,
                                        quote_instance,
                                        exchange,
                                        api_name,
                                        )

    def return_bittrex_pair_data_dict(self, raw_pair_data, exchange):
        """
        Takes the raw response data for one pair of Bittrex, calls an exchange-specific
        function on it which will make it into a nicely formatted pair_data_dict.

        pair_data_dict format:
        {
        'base': <Currency instance>,
        'quote': <Currency instance>,
        'exchange': <Exchange object to which current data relates>,
        'api_name': <pair name used for api calls, as string>,
        }
        """
        base_name = raw_pair_data['BaseCurrencyLong']
        quote_name = raw_pair_data['MarketCurrencyLong']
        base_name = correct_currency_name(base_name)
        quote_name = correct_currency_name(quote_name)
        base_instance = self.get_currency_instance(base_name)
        quote_instance = self.get_currency_instance(quote_name)
        api_name = raw_pair_data['MarketName']
        return self.form_pair_data_dict(base_instance,
                                        quote_instance,
                                        exchange,
                                        api_name,
                                        )

    def return_kraken_pair_data_dict(self, raw_pair_data, exchange):
        """
        Takes the raw response data for one pair of Kraken, calls an exchange-specific
        function on it which will make it into a nicely formatted pair_data_dict.

        pair_data_dict format:
        {
        'base': <Currency instance>,
        'quote': <Currency instance>,
        'exchange': <Exchange object to which current data relates>,
        'api_name': <pair name used for api calls, as string>,
        }
        """
        print(f"\nreturn_kraken_pair_data_dict\nraw_pair_data:\n{raw_pair_data}")
        base_code = raw_pair_data['base']
        base_code = self.convert_kraken_code_code(base_code)
        print(f"\nbase_code: {base_code}\n")
        quote_code = raw_pair_data['quote']
        quote_code = self.convert_kraken_code_code(quote_code)
        print(f"\nquote_code: {quote_code}\n")
        base_instance = Code.objects.get(code=base_code).currency
        quote_instance = Code.objects.get(code=quote_code).currency
        api_name = raw_pair_data['altname']
        return self.form_pair_data_dict(base_instance,
                                        quote_instance,
                                        exchange,
                                        api_name,
                                        )

    def form_pair_data_dict(self, base, quote, exchange, api_name):
        """
        {
        'base': <Currency instance>,
        'quote': <Currency instance>,
        'exchange': <Exchange object to which current data relates>,
        'api_name': <pair name used for api calls, as string>,
        }
        """
        return {
            'base': base,
            'quote': quote,
            'exchange': exchange,
            'api_name': api_name,
        }

    def add_pair_to_db(self, pair_data_dict, exchange):
        """

        Takes a pair data dict. Checks if the data is already in the Database.

        First checks if pair api name is already in the DB.
        - If not, it adds it.
        - Else it adds the exchange to it.

        Then it checks if the pair itself is added as TradablePair.
        - If not in DB: saves the pair to the DB
        - If already in DB: adds the current exchange to the pair.
        """
        pair_api_name_instance = self.handle_pair_api_name(pair_data_dict, exchange)
        try:
            pair = TradablePair.objects.get(base=pair_data_dict['base'],
                                            quote=pair_data_dict['quote'],
                                            )
        except TradablePair.DoesNotExist:
            pair = TradablePair(base=pair_data_dict['base'],
                                quote=pair_data_dict['quote'],
                                )
            pair.save()
        pair.exchanges.add(exchange)
        pair.api_names.add(pair_api_name_instance)

    def handle_pair_api_name(self, pair_data_dict, exchange):
        """
        Checks if pair api name is already in the DB. If not, it adds it. Also adds current
        exchange to current pair name.
        """
        try:
            pair_api_name = PairApiName.objects.get(name=pair_data_dict['api_name'])
        except PairApiName.DoesNotExist:
            pair_api_name = PairApiName(name=pair_data_dict['api_name'])
            pair_api_name.save()
        pair_api_name.exchanges.add(exchange)
        return pair_api_name

    def get_currency_instance(self, currency_name):
        print(f"\nget_currency_instance - currency_name: {currency_name} - currency_name length: {len(currency_name)})")
        return Currency.objects.get(name=currency_name)

    def convert_kraken_code_code(self, kraken_code_code):
        """
        Takes a code name from kraken, returns 'normal' code name. Kraken often puts an Z or X
        in front of their codenames, this will be removed.
        """
        kraken_code_tuple = (
            'ZCAD',
            'ZEUR',
            'ZGBP',
            'ZJPY',
            'ZUSD',
            'XETC',
            'XETH',
            'XICN',
            'XLTC',
            'XMLN',
            'XREP',
            'XXBT',
            'XXDG',
            'XXLM',
            'XXMR',
            'XXRP',
            'XZEC',
        )
        if kraken_code_code in kraken_code_tuple:
            return kraken_code_code[1:]
        else:
            return kraken_code_code
