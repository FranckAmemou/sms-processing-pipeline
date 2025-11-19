"""
Convertisseur de devises
"""

import requests
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger()

class CurrencyConverter:
    def __init__(self):
        self.rates = {}
        self.last_update = None
        self.base_currency = 'XOF'  # Devise de base pour les soldes

    def get_exchange_rates(self):
        """Récupère les taux de change actuels"""
        try:
            # Utilisation d'une API gratuite de taux de change
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.rates = data['rates']
                self.last_update = datetime.now()
                logger.info("Taux de change mis à jour avec succès")
                return True
        except Exception as e:
            logger.warning(f"Erreur récupération taux de change: {e}")

        # Taux de change fallback (approximatifs)
        self.rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'XOF': 600.0,  # 1 USD ≈ 600 XOF
            'FCFA': 600.0
        }
        logger.info("Utilisation des taux de change fallback")
        return False

    def convert_amount(self, amount, from_currency, to_currency):
        """Convertit un montant d'une devise à une autre"""
        if amount is None or amount == 0:
            return amount

        # Normaliser les codes de devise
        from_currency = self.normalize_currency_code(from_currency)
        to_currency = self.normalize_currency_code(to_currency)

        # Si les devises sont identiques, pas de conversion
        if from_currency == to_currency:
            return amount

        # S'assurer que les taux sont à jour
        if not self.rates or not self.last_update or (datetime.now() - self.last_update).days > 0:
            self.get_exchange_rates()

        # Conversion via USD comme devise intermédiaire
        try:
            # Convertir de la devise source vers USD
            if from_currency != 'USD':
                if from_currency in self.rates:
                    amount_in_usd = amount / self.rates[from_currency]
                else:
                    logger.warning(f"Devise source non trouvée: {from_currency}")
                    return amount
            else:
                amount_in_usd = amount

            # Convertir de USD vers la devise cible
            if to_currency != 'USD':
                if to_currency in self.rates:
                    converted_amount = amount_in_usd * self.rates[to_currency]
                else:
                    logger.warning(f"Devise cible non trouvée: {to_currency}")
                    return amount
            else:
                converted_amount = amount_in_usd

            # Arrondir à 2 décimales
            converted_amount = round(converted_amount, 2)

            logger.debug(f"Conversion: {amount} {from_currency} → {converted_amount} {to_currency}")
            return converted_amount

        except Exception as e:
            logger.error(f"Erreur lors de la conversion: {e}")
            return amount

    def normalize_currency_code(self, currency):
        """Normalise les codes de devise"""
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

# Instance globale du convertisseur
currency_converter = CurrencyConverter()