"""
Parseurs pour les données financières (dates, montants, etc.)
"""

import re
from datetime import datetime
from .validators import is_valid_phone_number, is_valid_counterparty_name
from utils.logger import setup_logger

logger = setup_logger(__name__)

def normalize_date(date_str):
    """
    Normalise une date au format YYYY-MM-DD
    
    Args:
        date_str: Chaîne de date dans différents formats
        
    Returns:
        str: Date normalisée au format YYYY-MM-DD, ou None si invalide
    """
    if not date_str or not isinstance(date_str, str):
        return None

    date_str = date_str.strip()
    
    try:
        # Si la date est déjà au format YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            # Valider que c'est une date valide
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str

        # Si la date est au format DD/MM/YYYY
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
            day, month, year = date_str.split('/')
            # S'assurer que les composants ont 2 chiffres
            day = day.zfill(2)
            month = month.zfill(2)
            normalized = f"{year}-{month}-{day}"
            # Valider la date
            datetime.strptime(normalized, '%Y-%m-%d')
            return normalized

        # Si la date est au format DD-MM-YYYY
        elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', date_str):
            day, month, year = date_str.split('-')
            day = day.zfill(2)
            month = month.zfill(2)
            normalized = f"{year}-{month}-{day}"
            datetime.strptime(normalized, '%Y-%m-%d')
            return normalized

        # Si la date est au format YYYY/MM/DD
        elif re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
            year, month, day = date_str.split('/')
            month = month.zfill(2)
            day = day.zfill(2)
            normalized = f"{year}-{month}-{day}"
            datetime.strptime(normalized, '%Y-%m-%d')
            return normalized

        # Format avec heures : "2025-09-09 13:51:23"
        elif re.match(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$', date_str):
            date_part = date_str.split()[0]
            datetime.strptime(date_part, '%Y-%m-%d')
            return date_part

        # Format avec heures : "09/09/2025 13:51:23"
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}\s+\d{2}:\d{2}:\d{2}$', date_str):
            date_part = date_str.split()[0]
            day, month, year = date_part.split('/')
            day = day.zfill(2)
            month = month.zfill(2)
            normalized = f"{year}-{month}-{day}"
            datetime.strptime(normalized, '%Y-%m-%d')
            return normalized

        # Format "LE 2025-09-09"
        elif re.match(r'^LE\s+\d{4}-\d{2}-\d{2}$', date_str, re.IGNORECASE):
            date_part = date_str.split()[1]
            datetime.strptime(date_part, '%Y-%m-%d')
            return date_part

        # Format "LE 09/09/2025"
        elif re.match(r'^LE\s+\d{1,2}/\d{1,2}/\d{4}$', date_str, re.IGNORECASE):
            date_part = date_str.split()[1]
            day, month, year = date_part.split('/')
            day = day.zfill(2)
            month = month.zfill(2)
            normalized = f"{year}-{month}-{day}"
            datetime.strptime(normalized, '%Y-%m-%d')
            return normalized

    except ValueError as e:
        logger.warning(f"Date invalide '{date_str}': {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la normalisation de la date '{date_str}': {e}")
        return None

    logger.debug(f"Format de date non reconnu: {date_str}")
    return None

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

    # Gestion des séparateurs
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
            if len(parts[1]) in [1, 2]:
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
            if len(parts[1]) in [1, 2]:
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

def extract_numeric_value(text):
    """
    Extrait une valeur numérique d'un texte contenant du texte et des chiffres
    """
    if not text:
        return None
        
    # Chercher des motifs numériques
    patterns = [
        r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)',  # Nombres avec séparateurs
        r'(\d+)',  # Nombres simples
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, str(text))
        if matches:
            # Prendre le plus grand nombre trouvé (généralement le montant)
            numbers = [parse_currency_amount(match) for match in matches]
            valid_numbers = [n for n in numbers if n is not None and n > 0]
            if valid_numbers:
                return max(valid_numbers)
    
    return None