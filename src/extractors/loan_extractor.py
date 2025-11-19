import re
from core.parsers import parse_currency_amount


def extract_loan_total_due(normalized_body):
    """
    Extrait le montant total dû pour un prêt
    """
    patterns = [
                # Ajout des patterns avec "credit"
        r'CREDIT DE\s+([\d\s,]+)\s*FCFA',
        r'VOTRE CREDIT DE\s+([\d\s,]+)\s*FCFA',
        r'CREDIT\s+DE\s+([\d\s,]+)\s*FCFA',
                # NOUVEAU PATTERN pour "total: 100430 F"
        r'TOTAL:\s*([\d\s,]+)\s*F(?:\s|$|\.)',
        r'TOTAL\s*:\s*([\d\s,]+)\s*FCFA',
                # NOUVEAU PATTERN pour "dette de 13275FCFA"
        r'DETTE DE\s+([\d\s,]+)\s*FCFA',
        r'DETTE DE\s+([\d\s,]+)FCFA',
        r'DETTE DE\s+(\d+)\s*FCFA',
                #  NOUVEAUX PATTERNS POUR PLANS DE REMBOURSEMENT
        r'LA TOTALITE DES\s+([\d\s,]+)\s*FCFA',
        r'TOTAL A REMBOURSER\s*:\s*([\d\s,]+)\s*FCFA',
        r'SOMME TOTALE\s+([\d\s,]+)\s*FCFA',
        r'VOUS N.AVEZ PAS\s+([\d\s,]+)\s*FCFA',
        # Pattern en premier pour capturer "pret de 502156 FCFA"
        r'PRET DE\s+([\d\s,]+)\s*FCFA',
        r'VOTRE PRET DE\s+([\d\s,]+)\s*FCFA',
        r'RESTANT DU\s*:\s*([\d\s,]+)\s*XOF',
        r'RESTANT DU\s*:\s*([\d\s,]+)\s*FCFA',
        # Pattern spécifique Orange Bank
        r'NOUVEAU MONTANT A REMBOURSER:\s*([\d\s]+)\s*FCFA',
        r'MONTANT A REMBOURSER:\s*([\d\s]+)\s*FCFA',
        r'REMBOURSER:\s*([\d\s]+)\s*FCFA',
        r'RESTANT A REMBOURSER:\s*([\d\s]+)\s*FCFA'
        # Patterns pour le reste à rembourser
        r'RESTANT DU\s*:\s*([\d\s,]+)\s*XOF',
        r'RESTANT DU\s*:\s*([\d\s,]+)\s*FCFA',
        r'RESTANT DU\s*:\s*([\d\s,]+)\.',
        r'RESTANT DU\s*([\d\s,]+)\s*FCFA',
        r'RESTANT A REMBOURSER\s*:\s*([\d\s,]+)\s*FCFA',
        r'MONTANT RESTANT\s*:\s*([\d\s,]+)\s*FCFA',
        r'DU\s*:\s*([\d\s,]+)\s*FCFA',  # Format "Restant du: X FCFA"
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            amount_str = match.group(1).strip()
            amount_str = re.sub(r'\s+', '', amount_str)
            amount = parse_currency_amount(amount_str)
            if amount is not None:

                return amount

    return None

