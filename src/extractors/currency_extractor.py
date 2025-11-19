import re
# Ajouter en haut du fichier
from core.parsers import parse_currency_amount
from core.validators import is_valid_phone_number, is_valid_counterparty_name
def extract_currency(normalized_body):
    """Extrait la devise du message - VERSION CORRIGÉE ET TESTÉE"""
    if not normalized_body:
        return 'XOF'

    normalized_upper = normalized_body.upper()


    # Détection prioritaire des devises dans le contexte des montants
    currency_patterns = [
        # Patterns XOF avec "F" seul - PRIORITAIRES
        (r'RECU\s+[\d\s\.,]+\s*F(?:\s|$|[^A-Z])', 'XOF'),
        (r'SOLDE:\s*[\d\s\.,]+\s*F(?:\s|$|[^A-Z])', 'XOF'),
        (r'\d[\d\s\.,]*\s*F\s+DE\s+', 'XOF'),
        (r'\d[\d\s\.,]*\s*F\s+POUR:', 'XOF'),

        # Pattern général pour nombres suivis de F
        (r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\s*F(?:\s|$|[^A-Z])', 'XOF'),

        # Patterns XOF explicites
        (r'(?:PAIEMENT|PAYMENT)\s+(?:DE|OF)\s+[\d\s,\.]+\s+XOF', 'XOF'),
        (r'XOF\s+[\d\s,\.]+', 'XOF'),
        (r'FCFA\s+[\d\s,\.]+', 'XOF'),
        (r'\d[\d\s,\.]*\s+(?:XOF|FCFA|F\.)', 'XOF'),

        # Patterns pour USD
        (r'(?:PAIEMENT|PAYMENT)\s+(?:DE|OF)\s+[\d\s,\.]+\s+USD', 'USD'),
        (r'\d[\d\s,\.]*\s+USD', 'USD'),
        (r'USD\s+[\d\s,\.]+', 'USD'),
        (r'\$\s*\d', 'USD'),

        # Patterns pour EUR
        (r'(?:PAIEMENT|PAYMENT)\s+(?:DE|OF)\s+[\d\s,\.]+\s+EUR', 'EUR'),
        (r'\d[\d\s,\.]*\s+EUR', 'EUR'),
        (r'EUR\s+[\d\s,\.]+', 'EUR'),
        (r'€\s*\d', 'EUR'),
    ]

    for pattern, currency in currency_patterns:
        match = re.search(pattern, normalized_upper)
        if match:

            return currency

    # Fallback basé sur les mots-clés
    if re.search(r'USD|\$|DOLLAR', normalized_upper):

        return 'USD'
    elif re.search(r'EUR|€|EURO', normalized_upper):

        return 'EUR'
    elif re.search(r'XOF|FCFA|FRANC\s+CFA', normalized_upper):

        return 'XOF'
    elif re.search(r'\d[\d\s,\.]*\s*F(?:\s|$|[^A-Z])', normalized_upper):

        return 'XOF'


    return 'XOF'

def extract_balance_currency(normalized_body):
    """Extrait spécifiquement la devise du solde - VERSION AMÉLIORÉE"""
    normalized_upper = normalized_body.upper()

    balance_patterns = [
        (r'SOLDE.*XOF', 'XOF'),
        (r'SOLDE.*FCFA', 'XOF'),
        (r'NOUVEAU SOLDE.*XOF', 'XOF'),
        (r'NEW BALANCE.*XOF', 'XOF'),
        (r'SOLDE.*USD', 'USD'),
        (r'SOLDE.*\$', 'USD'),
        (r'SOLDE.*EUR', 'EUR'),
        (r'SOLDE.*€', 'EUR'),
        (r'BALANCE.*XOF', 'XOF'),
        (r'BALANCE.*USD', 'USD'),
        (r'BALANCE.*EUR', 'EUR'),
        (r'VOTRE SOLDE.*XOF', 'XOF'),
        (r'VOTRE SOLDE.*FCFA', 'XOF'),
        (r'VOTRE NOUVEAU SOLDE.*XOF', 'XOF'),
        (r'YOUR BALANCE.*XOF', 'XOF'),
    ]

    for pattern, currency in balance_patterns:
        if re.search(pattern, normalized_upper):
            return currency

    # Si pas de solde détecté, retourner None
    return None