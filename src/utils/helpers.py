import re

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

def extract_client_id(source_key):
    """Extrait l'ID client du SourceKey"""
    match = re.search(r'client_([a-f0-9-]+)', source_key)
    return match.group(1) if match else "unknown"

def extract_device_id(source_key):
    """Extrait l'ID device du SourceKey"""
    match = re.search(r'device_([a-f0-9]+)', source_key)
    return match.group(1) if match else "unknown"

def are_all_numeric_fields_null(amount, balance_after, loan_interest, tax_and_fee, loan_total_due):
    """
    Vérifie si tous les champs numériques importants sont nuls
    """
    return (
        (amount is None or amount == 0.0) and
        (balance_after is None or balance_after == 0.0) and
        (loan_interest is None or loan_interest == 0.0) and
        (tax_and_fee is None or tax_and_fee == 0.0) and
        (loan_total_due is None or loan_total_due == 0.0)
    )
def is_valid_phone_number(phone):
    """Valide si une chaîne est un numéro de téléphone valide"""
    if not phone or not isinstance(phone, str):
        return False

    phone_clean = re.sub(r'[^\d]', '', phone)
    if len(phone_clean) < 8 or len(phone_clean) > 15:
        return False
    if not phone_clean.isdigit():
        return False
    return True

def is_valid_counterparty_name(name):
    """Valide si un nom de contrepartie est plausible"""
    if not name or len(name) < 2:
        return False

    excluded_words = [
        'EST', 'SUR', 'VOTRE', 'COMPTE', 'MOBILE', 'MONEY', 'DE', 'PAR',
        'LE', 'LA', 'LES', 'UN', 'UNE', 'DES', 'DU', 'AU', 'AUX', 'ET','FCFA', 'XOF', 'SOLDE', 'NOUVEAU', 'DATE', 'ID', 'TRANSACTION',
        'REF', 'SUCCES', 'SUCCESS', 'EFFECTUE', 'AVEC', 'VOUS', 'AVEZ','RECU', 'DEBIT', 'CREDIT', 'FRAIS', 'DISCOUNT', 'BENEFICIE', 'D\'UN',
        'MESSAGE', 'SENDER', 'FINANCIAL', 'BALANCE', 'YOUR', 'NEW', 'FROM','VOTRE COMPTE MOBILE MONEY', 'COMPTE MOBILE MONEY', 'MOBILE MONEY',
        'SOLDE DISPONIBLE', 'DISPONIBLE', 'VIA L\'AGENT', 'UNE SOMME','AVEZ RETIRE', 'RETIRE', 'SOMME', 'A','MOOV MONEY EST DE','VOTRE SOLDE EST DE', 'NOUVEAU SOLDE','SOLDE MOOV MONEY',
        'FLOOZ DU COMPTE','COMPTE PRINCIPAL','SOLDE FLOOZ','Contact 693502266','Contact','la part du','a ete effectue avec succes'
    ]

    name_upper = name.upper()
    if name_upper in excluded_words:
        return False

    if len(name_upper) >= 3 and not name_upper.isdigit():
        if re.search(r'\d{4}-\d{2}-\d{2}', name_upper):
            return False
        if re.search(r'\d{8,}', name_upper):
            return False
        if re.search(r'[A-Z]{2,}', name_upper):
            words = name_upper.split()
            valid_words = [w for w in words if w not in excluded_words]
            if valid_words:
                return True
    return False
