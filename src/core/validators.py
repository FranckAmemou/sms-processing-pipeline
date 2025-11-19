
"""
Validateurs pour les données extraites
"""

import re

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

def is_valid_amount(amount):
    """Valide si un montant est plausible"""
    if amount is None:
        return False
    try:
        float_amount = float(amount)
        return -10000000 <= float_amount <= 10000000  # Plage raisonnable
    except (ValueError, TypeError):
        return False

def is_valid_reference(ref):
    """Valide si une référence est plausible"""
    if not ref or len(ref) < 4:
        return False

    ref_upper = ref.upper()

    # Exclure les montants avec devise
    if re.match(r'^\d+[A-Z]{3,4}$', ref_upper):
        return False

    # Exclure les termes communs
    excluded_terms = [
        'MASTERCARD', 'VISA', 'CARTE', 'CARD', 'DEBIT', 'CREDIT',
        'ACHAT', 'TPE', 'ONLINE', 'CHEZ', 'SUR', 'COMPTE', 'SOLDE',
        'FCFA', 'XOF', 'USD', 'EUR', 'ALERTE', 'DATE', 'HEURE', 'APPLE',
        'BILL', 'GLOVO', 'ORANGE', 'MTN', 'MOOV', 'WAVE', 'FLOOZ', 'MOMO',
        'MOBILE', 'MONEY', 'BANK', 'BANQUE', 'OPERATION', 'TRANSACTION',
        'SUCCES', 'REF', 'REFERENCE', 'ID', 'NUMERO', 'CODE',
        # AJOUT DES MOTS FRANÇAIS COMMUNS DANS LES ALERTES DE PRÊT
        'REMBOURSER', 'REMBOURSEZ', 'REMBOURSEMENT', 'ALIMENTEZ', 'ALIMENTEZ',
        'PENALITE', 'RISQUEZ', 'DEMAIN', 'SINON', 'VOUS', 'VOTRE', 'DES', 'UNE',
        'PRET', 'CREDIT', 'EMPRUNT', 'ECHEANCE', 'JOURS', 'RETARD', 'OBTENIR',
        'RISQUE', 'MAINTENANT', 'AUSSI', 'BIENTOT', 'DOIT', 'ETRE', 'AVANT',
        'APRES', 'POUR', 'AVEC', 'SANS', 'TOUJOURS', 'MAINTENANT'
    ]

    if ref_upper in excluded_terms:
        return False

    # EXCLURE LES DATES ET HEURES
    if re.match(r'^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$', ref):
        return False
    if re.match(r'^\d{1,2}:\d{2}$', ref):
        return False

    #  VALIDATION DES NOMBRES PURS
    if ref.isdigit():
        if len(ref) < 8:  # Les nombres de moins de 8 chiffres ne sont pas des références
            return False
        else:
            # Les nombres de 8 chiffres ou plus pourraient être des références
            return True

    # EXCLURE LES NUMÉROS DE CARTE
    if re.match(r'^\d{16}$', ref):
        return False

    #  VALIDATION POUR UUID (acceptés comme références valides)
    if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', ref, re.IGNORECASE):
        return True

    # VALIDATION POUR RÉFÉRENCES HEXADÉCIMALES (BNI, etc.)
    if re.match(r'^[A-F0-9]{8,16}$', ref):
        return True

    #  DOIT CONTENIR DES LETTRES ET DES CHIFFRES (sauf cas particuliers)
    has_letters = re.search(r'[A-Z]', ref, re.IGNORECASE)
    has_digits = re.search(r'\d', ref)

    if has_letters and has_digits:
        return True

    #  OU BIEN ÊTRE UNE LONGUE SÉQUENCE ALPHANUMÉRIQUE
    if len(ref) >= 8 and (has_letters or has_digits):
        return True

    # ACCEPTER LES UUID MÊME SANS CHIFFRES DANS CERTAINES PARTIES
    if '-' in ref and len(ref) >= 20:
        parts = ref.split('-')
        if len(parts) == 5 and all(3 <= len(part) <= 12 for part in parts):
            return True

    return False