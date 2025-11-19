import re
from datetime import datetime, timedelta

def extract_operation_date(normalized_body):
    """Extrait la date d'opération du message SMS - VERSION COMPLÈTE AVEC EXCLUSION DES PRÊTS"""

    # Exclure les dates dans les contextes de prêt
    normalized_upper = normalized_body.upper()

    # Si c'est un message de prêt, NE PAS extraire de date d'opération
    if any(loan_word in normalized_upper for loan_word in [
        'PRET', 'LOAN', 'EMPRUNT', 'ECHEANCE', 'REMBOURSEMENT', 'PENALITE'
    ]):

        return None

    # PATTERNS POUR DATES D'OPÉRATION (uniquement pour les transactions normales)
    date_patterns = [
        r'DATE[:\s]*(\d{2}-\d{2}-\d{4})\s+\d{2}:\d{2}:\d{2}',
        r'(\d{2}-\d{2}-\d{4})\s+\d{2}:\d{2}:\d{2}',
        r'(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}:\d{2}',
        r'(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}',
        # Format "le 2025-09-09" (priorité haute)
        r'LE\s+(\d{4}-\d{2}-\d{2})(?=\s+\d{2}:\d{2}:\d{2}|\s+SOLDE|\s|$)',
        r'LE\s+(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}',

        # Format "2025-09-09" seul
        r'(\d{4}-\d{2}-\d{2})(?=\s+\d{2}:\d{2}:\d{2}|\s+SOLDE|\s|$)',

        # Format avec heures "2025-09-09 13:51:23"
        r'(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}',

        # Format français "09/09/2025"
        r'LE\s+(\d{2}/\d{2}/\d{4})',
        r'(\d{2}/\d{2}/\d{4})(?=\s+\d{2}:\d{2}:\d{2}|\s+SOLDE|\s|$)',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, normalized_body)
        if match:
            date_str = match.group(1).strip()

            # Normaliser la date au format YYYY-MM-DD
            normalized_date = normalize_date(date_str)
            if normalized_date:

                return normalized_date


    return None


def extract_loan_deadline(normalized_body, received_at=None):
    """Extrait la date limite de remboursement - VERSION CORRIGÉE POUR ÉVITER LES DATES PAR DÉFAUT"""

    # TOUS LES PATTERNS POSSIBLES POUR LES DATES DE PRÊT
    echeance_patterns = [
        # Pattern pour "avant le 05/03/2023"
        r'avant le\s+(\d{2}/\d{2}/\d{4})',
        r'avant\s+le\s+(\d{2}/\d{2}/\d{4})',

        # Pattern pour "Echeance: 21/08/2025"
        r'ECHEANCE:\s*(\d{2}/\d{2}/\d{4})',
        r'ECHEANCE\s*:\s*(\d{2}/\d{2}/\d{4})',

        # Patterns pour autres formats
        r'ARRIVE A ECHEANCE LE\s+(\d{2}/\d{2}/\d{4})',
        r'ARRIVE A ECHEANCE\s+LE\s+(\d{2}/\d{2}/\d{4})',
        r'ECHEANCE LE\s+(\d{2}/\d{2}/\d{4})',
        r'ECHEANCE:\s+(\d{2}/\d{2}/\d{4})',
        r'A ECHEANCE LE\s+(\d{2}/\d{2}/\d{4})',

        # Patterns avec "jusqu'au"
        r'jusqu[\'\s]*au\s+(\d{2}/\d{2}/\d{4})',
        r'JUSQU[\'\s]*AU\s+(\d{2}/\d{2}/\d{4})',
        r'JUSQU[\'\s]*A\s+(\d{2}/\d{2}/\d{4})',

        # Pattern pour dates avec format "le 05/03/2023"
        r'LE\s+(\d{2}/\d{2}/\d{4})(?=\s*\.|\s*TEG|\s*REF|\s*$)',

        # Pattern générique pour toute date DD/MM/YYYY
        r'(\d{2}/\d{2}/\d{4})',
    ]

    for pattern in echeance_patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            normalized_date = normalize_date(date_str)
            if normalized_date:
                return normalized_date

    # DÉLAIS RELATIFS PRÉCIS (comme "Plus que 2 jours avant")
    if received_at:
        try:
            received_date = datetime.fromisoformat(received_at.replace('Z', '+00:00'))

            # Patterns pour délais relatifs EXPLICITES
            relative_patterns = [
                # Pattern pour "Plus que 2 jours avant"
                r"Plus que\s+(\d+)\s+jours?\s+avant",
                r"plus que\s+(\d+)\s+jours?\s+avant",
                r"(\d+)\s+jours?\s+avant l['eé]cheance",
                r"(\d+)\s+jours?\s+avant l['eé]ch[ée]ance",
                r"dans\s+(\d+)\s+jours?\s+avant",
                # Patterns généraux EXPLICITES
                r"plus que\s+(\d+)\s+jour",
                r"plus que\s+(\d+)\s+jours",
                r"(\d+)\s+jour\s+avant",
                r"(\d+)\s+jours\s+avant",
                r"dans\s+(\d+)\s+jour",
                r"dans\s+(\d+)\s+jours",
                r"(\d+)\s+jour\s+restant",
                r"(\d+)\s+jours\s+restants",
            ]

            for pattern in relative_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    days_until_due = int(match.group(1))
                    due_date = received_date + timedelta(days=days_until_due)
                    due_date_str = due_date.strftime("%Y-%m-%d")
                    return due_date_str

            # Seulement pour les contextes TRÈS spécifiques avec indication de délai
            if "aujourd'hui" in normalized_body.lower():
                due_date_str = received_date.strftime("%Y-%m-%d")
                return due_date_str
            elif "demain" in normalized_body.lower():
                due_date = received_date + timedelta(days=1)
                due_date_str = due_date.strftime("%Y-%m-%d")
                return due_date_str

        except Exception:
            # En cas d'erreur de calcul de date, on retourne None silencieusement
            pass

    return None


def normalize_date(date_str):
    """Normalise une date au format YYYY-MM-DD"""
    try:
        # Si la date est déjà au format YYYY-MM-DD
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str

        # Si la date est au format DD/MM/YYYY
        elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
            day, month, year = date_str.split('/')
            return f"{year}-{month}-{day}"

        # Si la date est au format DD-MM-YYYY
        elif re.match(r'\d{2}-\d{2}-\d{4}', date_str):
            day, month, year = date_str.split('-')
            return f"{year}-{month}-{day}"

    except Exception:
        # En cas d'erreur, retourner None silencieusement
        pass

    return None

