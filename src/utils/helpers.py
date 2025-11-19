
"""
Fonctions utilitaires réutilisables
"""

import re
from config.services import SERVICE_NAME_USED, IGNORE_KEYWORDS, ALWAYS_IGNORE_SENDERS

def should_ignore(row):
    """
    Vérifie si un SMS doit être ignoré
    """
    sender = str(row.get('Sender ID', '')).strip()
    body = str(row.get('Body', '')).lower()
    body_normalized = body.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('à', 'a')

    # Vérifier les senders à toujours ignorer
    sender_upper = sender.upper()
    if any(ignore_sender in sender_upper for ignore_sender in ALWAYS_IGNORE_SENDERS):
        return True

    # Vérifier si l'expéditeur est autorisé
    is_authorized_sender = any(
        authorized_service.upper() in sender_upper
        for authorized_service in SERVICE_NAME_USED
    )

    if not is_authorized_sender and sender:
        return True

    # Vérifier les mots-clés à ignorer
    if any(k.lower() in body for k in IGNORE_KEYWORDS):
        return True

    return False

def are_all_numeric_fields_null(amount, balance_after, loan_interest, tax_and_fee, loan_total_due):
    """Vérifie si tous les champs numériques importants sont nuls"""
    return (
        (amount is None or amount == 0.0) and
        (balance_after is None or balance_after == 0.0) and
        (loan_interest is None or loan_interest == 0.0) and
        (tax_and_fee is None or tax_and_fee == 0.0) and
        (loan_total_due is None or loan_total_due == 0.0)
    )

def extract_client_id(source_key):
    """Extrait l'ID client du SourceKey"""
    match = re.search(r'client_([a-f0-9-]+)', source_key)
    return match.group(1) if match else "unknown"

def extract_device_id(source_key):
    """Extrait l'ID device du SourceKey"""
    match = re.search(r'device_([a-f0-9]+)', source_key)
    return match.group(1) if match else "unknown"