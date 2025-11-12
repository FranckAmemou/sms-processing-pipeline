import requests
from datetime import datetime

class CurrencyConverter:
    def __init__(self):
        self.rates = {}
        self.last_update = None
        self.base_currency = 'XOF'

    def get_exchange_rates(self):
        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.rates = data['rates']
                self.last_update = datetime.now()
                return True
        except Exception:
            pass

        self.rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'XOF': 600.0,
            'FCFA': 600.0
        }
        return False

    def convert_amount(self, amount, from_currency, to_currency):
        if amount is None or amount == 0:
            return amount

        from_currency = self.normalize_currency_code(from_currency)
        to_currency = self.normalize_currency_code(to_currency)

        if from_currency == to_currency:
            return amount

        if not self.rates or not self.last_update or (datetime.now() - self.last_update).days > 0:
            self.get_exchange_rates()

        try:
            if from_currency != 'USD':
                if from_currency in self.rates:
                    amount_in_usd = amount / self.rates[from_currency]
                else:
                    return amount
            else:
                amount_in_usd = amount

            if to_currency != 'USD':
                if to_currency in self.rates:
                    converted_amount = amount_in_usd * self.rates[to_currency]
                else:
                    return amount
            else:
                converted_amount = amount_in_usd

            converted_amount = round(converted_amount, 2)
            return converted_amount

        except Exception:
            return amount

    def normalize_currency_code(self, currency):
        currency = currency.upper() if currency else 'XOF'
        mapping = {
            'FCFA': 'XOF',
            'F': 'XOF',
            '€': 'EUR',
            '$': 'USD',
            'EURO': 'EUR',
            'EUROS': 'EUR',
            'DOLLAR': 'USD',
            'DOLLARS': 'USD'
        }
        return mapping.get(currency, currency)

currency_converter = CurrencyConverter()