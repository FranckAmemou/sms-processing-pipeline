import re
from src.core.parsers import parse_currency_amount
from src.utils.logger import get_logger

logger = get_logger(__name__)

def extract_tax_and_fee(normalized_body):
    """
    Extrait les taxes et frais des transactions - VERSION PURIFIÉE
    """
    total_fees = 0.0
    normalized_upper = normalized_body.upper()

    is_pret_detaille = (
        "PRET ACCEPTE" in normalized_upper and
        "FRAIS" in normalized_upper and
        "TAXE" in normalized_upper and
        "MONTANT NET RECU" in normalized_upper
    )

    if is_pret_detaille:


        # STRATÉGIE 1: Extraction dynamique pour prêts (additionne TOUS les frais/taxes)
        frais_taxes_patterns = [
            # Pattern pour frais de mise en place (capture n'importe quel montant)
            r'FRAIS[^:]*:\s*([\d\s,]+)\s*FCFA',
            r'FRAIS[^:]*:\s*([\d\s,]+)\s*F',

            # Pattern pour taxe sur frais (capture n'importe quel montant)
            r'\+\s*TAXE\s*:\s*([\d\s,]+)\s*FCFA',
            r'TAXE\s*:\s*([\d\s,]+)\s*FCFA',
            r'TAXE\s*:\s*([\d\s,]+)\s*F',

            # Pattern pour taxe sur intérêts (capture n'importe quel montant)
            r'INTERETS[^:]*:\s*[\d\s,]+\.\s*TAXE:\s*([\d\s,]+)',
            r'INTERETS[^:]*:\s*[\d\s,]+\s*TAXE:\s*([\d\s,]+)',
        ]

        found_amounts = []
        for pattern in frais_taxes_patterns:
            matches = re.findall(pattern, normalized_upper)
            if matches:
                for match in matches:
                    amount = parse_currency_amount(match)
                    if amount and amount > 0 and amount not in found_amounts:
                        found_amounts.append(amount)
                        total_fees += amount


        # Si on a trouvé des frais pour le prêt, on retourne directement
        if total_fees > 0:
            return total_fees



    # Patterns SPÉCIFIQUES et UNIQUES (EXISTANTS)
    frais_patterns = [
        # Pattern pour Wave "Frais: 1.100F"
        r'FRAIS:\s*(\d+\.\d+)F',
        r'FRAIS\s*:\s*(\d+\.\d+)F',
        r'FRAIS\s+(\d+\.\d+)F',
        r'PENALITE:\s*([\d\s]+)\s*FCFA',
        r'PENALITES:\s*([\d\s]+)\s*FCFA',
        r'PENALITE\s*:\s*([\d\s]+)\s*FCFA',
        # Pattern pour frais de transfert international
        r'FRAIS=(\d+)\s*FCFA',
        r'FRAIS\s*=\s*(\d+)\s*FCFA',
        r'FRAIS\s*:\s*(\d+)\s*FCFA',
        r'COMMISSION DE LA TRANSACTION\s+([\d\s]+)\s*FCFA',
        r'COMMISSION\s+([\d\s]+)\s*FCFA',
        r'COMMISSION\s*:\s*([\d\s]+)\s*FCFA',
        r'TIMBRE:\s*([\d\s]+)\s*FCFA',
        r'TIMBRE\s*:\s*([\d\s]+)\s*FCFA',
        r'TIMBRE\s+([\d\s]+)\s*FCFA',

        r'FRAIS:\s*([\d\s]+)\s*FCFA',
        r'FRAIS\s*:\s*([\d\s]+)\s*FCFA',
        r'FEE:\s*([\d\s]+)\s*FCFA',
        r'LE COUT DE LA TRANSACTION\s+([\d\s,]+)\s*FCFA',
        r'COUT DE LA TRANSACTION\s+([\d\s,]+)\s*FCFA',
        r'FRAIS DE TRANSACTION\s+([\d\s,]+)\s*FCFA',
        r'COUT\s+([\d\s,]+)\s*FCFA',
        # Format "Cout de la transaction: 1547,00 FCFA"
        r'COUT DE LA TRANSACTION:\s*([\d\s,]+)\s*FCFA',
        r'COUT DE LA TRANSACTION\s*:\s*([\d\s,]+)\s*FCFA',
        r'COUT\s+DE\s+LA\s+TRANSACTION:\s*([\d\s,]+)\s*FCFA',
        r'COUT\s+TRANSACTION:\s*([\d\s,]+)\s*FCFA',
        r'COUT:\s*([\d\s,]+)\s*FCFA',

        r'FRAIS\s+(\d+)\s*FCFA',
        r'FRAIS\s+([\d\s,]+)\s*FCFA',
        r'FRAIS:\s*(\d+)\s*FCFA',
        r'FRAIS\s*:\s*(\d+)\s*FCFA',
        r'FRAIS:(\d+)F',           # "Frais:500F"
        r'FRAIS:\s*(\d+)\s*F',     # "Frais: 500 F"
        r'FRAIS:(\d+)FCFA',        # "Frais:500FCFA"
        r'FRAIS:\s*(\d+)\s*FCFA',
        # Pattern pour "Frais: 100 FCFA" (le plus spécifique)
        r'FRAIS:\s*(\d+)\s*FCFA',
        r'FRAIS\s*:\s*(\d+)\s*FCFA',
        r'FRAIS\s+(\d+)\s*FCFA',

        # Patterns généraux (moins spécifiques)
        r'FRAIS:\s*([\d\s,]+)\s*FCFA',
        r'FRAIS\s*:\s*([\d\s,]+)\s*FCFA',
        r'FEES:\s*([\d\s,]+)\s*FCFA',
    ]

    # Utiliser une variable pour suivre le premier match
    frais_trouves = False

    for pattern in frais_patterns:
        matches = re.findall(pattern, normalized_upper)
        if matches:
            # Prendre seulement le PREMIER match
            for match in matches:
                if not frais_trouves:
                    frais_amount = parse_currency_amount(match)
                    if frais_amount and frais_amount > 0:
                        total_fees = frais_amount
                        frais_trouves = True

                        break
            if frais_trouves:
                break

    # Vérifier les doublons dans d'autres fonctions
    if total_fees > 0:
        # Compter combien de fois "FRAIS" apparaît
        count_frais = normalized_upper.count('FRAIS')
        count_fees = normalized_upper.count('FEES')

        # Si plusieurs occurrences, prendre la première mention
        if count_frais > 1:
            # Extraire tous les montants après "FRAIS"
            all_frais_matches = re.findall(r'FRAIS[:\s]*([\d\s,]+)\s*FCFA', normalized_upper)
            if all_frais_matches:
                # Prendre le premier
                first_frais = parse_currency_amount(all_frais_matches[0])
                if first_frais and first_frais > 0:
                    total_fees = first_frais


    return total_fees if total_fees > 0 else None

  