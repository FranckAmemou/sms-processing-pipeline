
"""
Parseurs pour les différents formats de données
"""

import re
from datetime import datetime, timedelta
from validators import is_valid_phone_number, is_valid_counterparty_name
def parse_currency_amount(amount_str, default_value=0.0):
    """
    Parse un montant en devise de manière robuste - VERSION ULTRA ROBUSTE
    """
    if amount_str is None:
        return default_value

    # Convertir en chaîne
    if not isinstance(amount_str, str):
        try:
            return float(amount_str)
        except (ValueError, TypeError):
            return default_value

    original = amount_str.strip()
    if not original:
        return default_value

    # Supprimer les points finaux problématiques
    original = re.sub(r'\.\s*$', '', original)  # Point final suivi d'espace ou fin
    original = re.sub(r'\s+', ' ', original)    # Normaliser les espaces

    # Nettoyer et normaliser
    clean = re.sub(r'[^\d\.,\-]', '', original)

    if not clean or not any(c.isdigit() for c in clean):
        return default_value

    # Déterminer le signe
    is_negative = clean.startswith('-')
    if is_negative:
        clean = clean.lstrip('-')

    # Si pas de séparateur, conversion directe
    if '.' not in clean and ',' not in clean:
        try:
            result = float(clean)
            return -result if is_negative else result
        except ValueError:
            return default_value

    #  Gestion des séparateurs
    last_dot = clean.rfind('.')
    last_comma = clean.rfind(',')

    # Cas standard : un séparateur décimal clair
    if last_dot >= 0 and last_comma >= 0:
        # Les deux séparateurs présents
        if last_dot > last_comma:
            # Format: 1,234.56
            integer_part = clean[:last_dot].replace(',', '')
            decimal_part = clean[last_dot+1:]
        else:
            # Format: 1.234,56
            integer_part = clean[:last_comma].replace('.', '')
            decimal_part = clean[last_comma+1:]
    elif last_dot >= 0:
        # Uniquement des points
        parts = clean.split('.')
        if len(parts) == 2:
            # Accepter 1-2 chiffres décimaux
            if len(parts[1]) in [1, 2]:  # ← CHANGEMENT ICI
                # Format: 1234.5 ou 1234.56 (décimal)
                integer_part = parts[0]
                decimal_part = parts[1]
            else:
                # Format: 1.234.567 (milliers)
                integer_part = clean.replace('.', '')
                decimal_part = ''
        else:
            # Plus de 2 parties → milliers
            integer_part = clean.replace('.', '')
            decimal_part = ''
    elif last_comma >= 0:
        # Uniquement des virgules
        parts = clean.split(',')
        if len(parts) == 2:
            # Accepter 1-2 chiffres décimaux
            if len(parts[1]) in [1, 2]:  # ← CHANGEMENT ICI
                # Format: 1234,5 ou 1234,56 (décimal)
                integer_part = parts[0]
                decimal_part = parts[1]
            else:
                # Format: 1,234,567 (milliers)
                integer_part = clean.replace(',', '')
                decimal_part = ''
        else:
            # Plus de 2 parties → milliers
            integer_part = clean.replace(',', '')
            decimal_part = ''
    else:
        integer_part = clean
        decimal_part = ''

    # Nettoyer les parties
    integer_part = re.sub(r'[^\d]', '', integer_part)
    decimal_part = re.sub(r'[^\d]', '', decimal_part)

    # Reconstruire le nombre
    if integer_part or decimal_part:
        try:
            number_str = integer_part
            if decimal_part:
                number_str += '.' + decimal_part
            result = float(number_str)
            return -result if is_negative else result
        except ValueError:
            pass

    # Fallback final : extraire uniquement les chiffres
    try:
        digits_only = re.sub(r'[^\d]', '', original)
        if digits_only:
            result = float(digits_only)
            return -result if is_negative else result
    except ValueError:
        pass

    return default_value


def parse_phone_number(phone_str):
    """
    Parse et nettoie un numéro de téléphone
    """
    if not phone_str:
        return None
    
    # Supprimer tous les caractères non numériques
    clean_phone = re.sub(r'[^\d]', '', phone_str)
    
    # Valider la longueur
    if 8 <= len(clean_phone) <= 15:
        return clean_phone
    
    return None