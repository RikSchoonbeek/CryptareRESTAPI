import json
import requests

from django.core.management.base import BaseCommand

from exchange_rate.models import ApiMethod, Code, Currency, Exchange

from ._utils import correct_currency_name


class Command(BaseCommand):
    help = "Gets the tradable currencies from the Exchanges that we programmed"

    def handle(self, *args, **options):
        for exchange in Exchange.objects.all():
            self.get_data(exchange)

    def get_data(self, exchange):
        print(f"\n\n\n\nExchange = {exchange.name}\n\n")
        url = self.get_url(exchange)
        response = requests.get(url)
        response_dict = json.loads(response.text)
        print(f"response_dict:\n{response_dict}")
        self.handle_data(response_dict, exchange)

    def get_url(self, exchange):
        """
        Get's the api url needed for the specific exchange
        """
        bitstamp_url = ApiMethod.objects.get(
            short_name='Get tradable currency pair info',
            exchange__name='Bitstamp',
        ).url
        bittrex_url = ApiMethod.objects.get(
            short_name='Get currencies',
            exchange__name='Bittrex',
        ).url
        kraken_url = ApiMethod.objects.get(
            short_name='Get currencies',
            exchange__name='Kraken',
        ).url
        urls = {
            # https://www.bitstamp.net/api/v2/trading-pairs-info
            'Bitstamp': exchange.api_url + bitstamp_url,
            # https://bittrex.com/api/v1.1/public/getcurrencies
            'Bittrex': exchange.api_url + bittrex_url,
            # https://api.kraken.com/0/public/Assets
            'Kraken': exchange.api_url + kraken_url,
        }
        return urls[exchange.name]

    def handle_data(self, response_dict, exchange):
        if exchange.name == 'Bitstamp':
            self.handle_data_bitstamp(response_dict, exchange)
        if exchange.name == 'Bittrex':
            self.handle_data_bittrex(response_dict, exchange)
        if exchange.name == 'Kraken':
            self.handle_data_kraken(response_dict, exchange)

    def handle_data_bitstamp(self, response_dict, exchange):
        """
        Takes the raw response from the api call. Iterates over each currency in the raw data
        and delegates the further handling of that data.
        """
        for pair_data in response_dict:
            currency_data_dict_list = self.get_bitstamp_currency_data_dicts_in_list(
                pair_data,
                exchange,
            )
            for currency_data_dict in currency_data_dict_list:
                self.handle_currency_data_dict(currency_data_dict, exchange)

    def handle_data_bittrex(self, response_dict, exchange):
        # Loop over all currencies in response_dict['result']
        for currency_data in response_dict['result']:
            # Get currency_data_dict
            currency_data_dict = self.get_bittrex_currency_data_dict(currency_data,
                                                                     exchange,
                                                                     )
            self.handle_currency_data_dict(currency_data_dict, exchange)

    def handle_data_kraken(self, response_dict, exchange):
        # Loop over all currencies in response_dict['result']
        for key, currency_data in response_dict['result'].items():
            # Get currency_data_dict
            currency_data_dict = self.get_kraken_currency_data_dict(currency_data,
                                                                    exchange,
                                                                    )
            self.handle_currency_data_dict(currency_data_dict, exchange)
        pass

    def get_bittrex_currency_data_dict(self, raw_currency_data, exchange):
        """
        Takes the raw currency data of a Bittrex api call. Outputs it as a dict in the
        following format:

        {
        'name': <currency name>,
        'type': <currency type>,
        'code': <currency code for current exchange>,
        'exchange': <exchange for which code applies>,
        }
        """
        uncorrected_currency_name = raw_currency_data['CurrencyLong']
        corrected_currency_name = correct_currency_name(uncorrected_currency_name)
        return {
            'name': corrected_currency_name,
            'type': self.get_currency_type(corrected_currency_name),
            'code': raw_currency_data['Currency'],
            'exchange': exchange,
        }

    def get_kraken_currency_data_dict(self, raw_currency_data, exchange):
        """
        Takes the raw currency data of a Kraken api call. Outputs it as a dict in the
        following format:

        {
        'name': <currency name>,
        'type': <currency type>,
        'code': <currency code for current exchange>,
        'exchange': <exchange for which code applies>,
        }
        """
        print(f"raw_currency_data:\n{raw_currency_data}")
        currency_code = raw_currency_data['altname']
        currency_name = correct_currency_name(currency_code)
        return {
            'name': currency_name,
            'type': self.get_currency_type(currency_name),
            'code': currency_code,
            'exchange': exchange,
        }

    def handle_currency_data_dict(self, currency_data_dict, exchange):
        """
        Takes a currency data dict. Calls add_currency_to_db and add_code_to_db on it.
        """
        currency = self.add_currency_to_db(currency_data_dict)
        self.add_code_to_db(currency_data_dict, currency, exchange)

    def add_currency_to_db(self, currency_data_dict):
        """
        Takes a currency data dict and checks if that currency is already in the DB or not.

        - If not in DB: add it
        - If already in DB: do nothing.
        """
        try:
            currency = Currency.objects.get(name=currency_data_dict['name'])
        except Currency.DoesNotExist:
            currency = None

        if not currency:
            currency = Currency(
                name=currency_data_dict['name'],
                type=currency_data_dict['type'],
            )
            currency.save()

        return currency

    def add_code_to_db(self, currency_data_dict, currency, exchange):
        """
        Takes a currency data dict and checks if that code is already in the DB or not.

        - If not in DB: add that code to the db
        - If already in DB: add current exchange to code in DB
        """
        try:
            code = Code.objects.get(code=currency_data_dict['code'])
        except Code.DoesNotExist:
            code = None

        if not code:
            code = Code(
                code=currency_data_dict['code'],
                currency=currency,
            )
            code.save()
            code.exchange.add(exchange)
            code.save()
        else:
            print(f"Attemting to add new exchange for code {code.code}")
            code.exchange.add(exchange)

    def get_bitstamp_currency_data_dicts_in_list(self, pair_info, exchange):
        """
        Get the raw pair data from the Bitstamp API response. Return an iterable of two
        currency data dicts.
        """
        names = pair_info['description'].split(' / ')
        codes = pair_info['name'].split('/')

        for index, name in enumerate(names):
            names[index] = correct_currency_name(name)

        currency_data_dicts = [
            {
                'name': names[0],
                'code': codes[0],
                'type': self.get_currency_type(names[0]),
                'exchange': exchange,
            },
            {
                'name': names[1],
                'code': codes[1],
                'type': self.get_currency_type(names[1]),
                'exchange': exchange,
            },
        ]
        return currency_data_dicts

    def get_currency_type(self, currency_name):
        print("get_currency_type")
        print(f"currency name: {currency_name}")
        crypto = [
            '0x Protocol', '2GIVE', 'Ada', 'AdEx', 'adToken', 'Aeon', 'AidCoin', 'Apx',
            'Aragon', 'Ardor', 'Ark', 'ArtByte', 'Augur', 'AuroraCoin', 'Bancor',
            'Basic Attention Token', 'BitBay', 'BitBean', 'BitCNY', 'Bitcoin', 'Bitcoin',
            'Bitcoin Cash', 'Bitcoin Cash', 'Bitcoin Gold', 'Bitcoin Private', 'BitcoinDark',
            'BitCrystals', 'BitSend', 'BitShares', 'Bitswift', 'BitTube', 'BlackCoin',
            'Blitzcash', 'BlockMason Credit Protocol', 'Blocknet', 'Blocktix', 'BLOCKv',
            'Bloom', 'Breakout', 'Breakout Stake', 'BURST', 'Bytecent', 'Bytes',
            'CannabisCoin', 'CapriCoin', 'CashBet', 'Chronobank Time', 'Circuits of Value', 'Civic',
            'CLAMs', 'CloakCoin', 'ClubCoin', 'Cofound.it', 'Counterparty', 'CreditBit',
            'Crown', 'CureCoin', 'Dash', 'Databits', 'DECENT', 'Decentraland', 'Decred',
            'Diamond', 'Digibyte', 'DigitalNote', 'Digix DAO', 'district0x', 'DMarket',
            'Dogecoin', 'DopeCoin', 'Dynamic', 'eBoost', 'Edgeless', 'Einsteinium', 'Elastic',
            'ElectronicGulden', 'EmerCoin', 'EnergyCoin', 'Enigma', 'EOS', 'Ethereum',
            'Ethereum Classic', 'EuropeCoin', 'EverGreenCoin', 'ExclusiveCoin', 'Expanse',
            'Factom', 'FairCoin', 'Feathercoin', 'Firstblood', 'Florin', 'FoldingCoin',
            'FunFair', 'Gambit', 'GameCredits', 'Gbg', 'GeoCoin', 'Gifto',
            'GlobalCurrencyReserve', 'Gnosis', 'GoldCoin', 'Golem', 'Golos', 'GridCoin',
            'Groestlcoin', 'Gulden', 'Guppy', 'HempCoin', 'Humaniq', 'I/OCoin', 'Iconomi', 'IDNI Agoras',
            'iEx.ec', 'Ignis', 'Incent', 'InfluxCoin', 'Internet Of People', 'Ion', 'Komodo',
            'Kore', 'LBRY Credits', 'Legends', 'Lisk', 'Litecoin', 'Litecoin', 'Lomocoin',
            'Loopring', 'Lumen', 'Lunyr', 'Magi', 'MaidSafeCoin', 'Melon', 'Memetic',
            'Mercury', 'METAL', 'Monaco', 'MonaCoin', 'Monero', 'MonetaryUnit', 'Musicoin',
            'Myriad', 'Mysterium', 'Naga', 'Namecoin', 'NAVCoin', 'NEM', 'Neo', 'NeosCoin', 'Nexium',
            'Nexus', 'Nubits', 'Numeraire', 'Nxt', 'Odyssey', 'OkCash', 'OmiseGO', 'OmniCoin',
            'ParkByte', 'Particl', 'Patientory', 'Peercoin', 'PesetaCoin', 'PinkCoin', 'Pivx',
            'Polymath', 'PotCoin', 'PowerLedger', 'Prime-XI', 'Project Decorum', 'Propy',
            'Qtum', 'Quantum Resistant Ledger', 'Qwark', 'Radium', 'ReddCoin', 'RevolutionVR',
            'Ripio Credit Network', 'Ripple', 'Rise', 'RubyCoin', 'SafeExchangeCoin',
            'Salt', 'SaluS', 'Sequence', 'Shift', 'Siacoin', 'Siberian Chervonets',
            'SingularDTV', 'Sirin Token', 'SolarCoin', 'Sphere', 'SpreadCoin', 'StartCoin',
            'Status Network Token', 'Stealth', 'Steem', 'SteemDollars', 'Stellar', 'STORJ', 'Storm',
            'Stratis', 'Swarm City Token', 'Syndicate', 'SynereoAmp', 'Synergy', 'SysCoin',
            'TenX Pay Token', 'Tether', 'The DAO', 'TokenCard', 'Tokes', 'TransferCoin', 'TRIG Token',
            'Tron', 'TrueUSD', 'Trustcoin', 'TrustPlus', 'Ubiq', 'UnbreakableCoin',
            'UnikoinGold', 'UpToken', 'Vcash', 'Verge', 'VeriCoin', 'Verium', 'Vertcoin',
            'ViaCoin', 'Viberate', 'vTorrent', 'Waves', 'WhiteCoin', 'Wings DAO',
            'Worldwide Asset Exchange', 'Zcash', 'Zclassic', 'ZCoin', 'ZenCash',
        ]
        fiat = [
            'British Pound',
            'Canadian Dollar',
            'Euro',
            'Japanese Yen',
            'US Dollar'
        ]
        if currency_name in crypto:
            return 'C'
        elif currency_name in fiat:
            return 'F'
        else:
            return self.currency_type_not_found(currency_name)

    def currency_type_not_found(self, currency_name):
        print(f"\n\nCurrent currency not found in current list.")
        print(f"Current currency: {currency_name}")
        while True:
            print(
                f"""You have the following options:
                1) Print list of known cryptocurrencies
                2) Print list of known fiat currencies
                3) Enter current currency type"""
            )
            user_choice = int(input("Enter choice (1, 2 or 3): "))
            if user_choice == 1:
                print(f"\n\nList of known cryptocurrencies:\n{crypto}")
            elif user_choice == 2:
                print(f"\n\nList of known fiat currencies:\n{fiat}")
            elif user_choice == 3:
                currency_type = ''
                while currency_type.upper() not in ('C', 'F'):
                    print("Choose current currency type:\nC - for crypto\nF - for fiat")
                    print(f"Current currency: {currency_name}")
                    currency_type = input("Enter currency type: ").upper()
                return 'C' if currency_type == 'C' else 'F'

    # def handle_data_bitstamp(self, response_dict, exchange):
    #     for pair_info in response_dict:
    #         # there are two currencies
    #         # check for both if it is in the database already
    #         # get key value of currency 1 and check for it in DB
    #         currency_data_list = self.get_currency_data_bitstamp(pair_info)
    #         for currency_data in currency_data_list:
    #             if self.check_if_currency_in_db(currency_data[0]):
    #                 self.add_code_to_db(currency_data, exchange)
    #             else:
    #                 self.add_currency_to_db(currency_data, exchange)
    #         #  get key value of currency 2 and check for it in DB
    #         # if not, save it to the database
    #         #pair_info['name']

    # def get_currency_data_bitstamp(self, pair_info):
    #     names = pair_info['description'].split(' / ')
    #     codes = pair_info['name'].split('/')
    #
    #     for index, name in enumerate(names):
    #         names[index] = self.correct_currency_name(name)
    #
    #     currency_data_list = [
    #         [
    #             names[0], codes[0], self.get_currency_type(names[0]),
    #         ],
    #         [
    #             names[1], codes[1], self.get_currency_type(names[1]),
    #         ],
    #     ]
    #
    #     return currency_data_list

    # def handle_data_bittrex(self, response_dict, exchange):
    #     crypto_data = response_dict['result']
    #     for currency in crypto_data:
    #         name = currency['CurrencyLong'].rstrip()
    #         code = currency['Currency']
    #         c_type = self.get_currency_type(name)
    #         currency_data = (name, code, c_type)
    #         currency = self.check_if_currency_in_db(name)
    #         if currency:
    #             self.add_code_to_db(currency_data, exchange)
    #         else:
    #             self.add_currency_to_db(currency_data, exchange)
    #
    # def handle_data_kraken(self, response_dict, exchange):
    #     crypto_data = response_dict['result']
    #     for currency_code, currency_data in crypto_data.items():
    #         pass
    #         #print(currency_data['altname'])

    # def add_code_to_db(self, currency_data, exchange, currency=None):
    #     try:
    #         code = Code.objects.get(code=currency_data[1])
    #         print(f"Code {code.code} already in DB:")
    #     except Code.DoesNotExist:
    #         code = None
    #     if not code:
    #         if not currency:
    #             currency = Currency.objects.get(name=currency_data[0])
    #         new_code = Code(code=currency_data[1],
    #                         currency=currency,
    #                         )
    #         new_code.save()
    #         new_code.exchange.add(exchange)
    #         print(f"Code {new_code.code} added to DB:")

    # def check_if_currency_in_db(self, currency_name):
    #     currency = None
    #     try:
    #         currency = Currency.objects.get(name=currency_name)
    #     except Currency.DoesNotExist:
    #         currency = None
    #     return currency
    #
    # def add_currency_to_db(self, currency_data, exchange):
    #     print(f"name: {currency_data[0]}")
    #     print(f"type: {currency_data[2]}")
    #     new_currency = Currency(
    #         name=currency_data[0],
    #         type=currency_data[2],
    #     )
    #     new_currency.save()
    #     print(f"New currency {currency_data[0]} added to DB.")
    #     self.add_code_to_db(currency_data, exchange, new_currency)


