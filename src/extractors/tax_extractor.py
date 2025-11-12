import re
from utils.helpers import parse_currency_amount

class TaxExtractor:
    
    def extract(self, normalized_body):
        """
        Extrait les taxes et frais des transactions - VERSION COMPLÈTEMENT CORRIGÉE
        """
        total_fees = 0.0
        normalized_upper = normalized_body.upper()

        # Patterns SPÉCIFIQUES et UNIQUES
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
                    if not frais_trouves:  # Si aucun frais n'a été trouvé encore
                        frais_amount = parse_currency_amount(match)
                        if frais_amount and frais_amount > 0:
                            total_fees = frais_amount   # pas additionner
                            frais_trouves = True
                            break  # Sortir de la boucle interne
                if frais_trouves:
                    break  # Sortir de la boucle externe

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

    def extract_tax_only(self, normalized_body):
        """
        Extrait spécifiquement les taxes (distinctes des frais)
        """
        normalized_upper = normalized_body.upper()
        tax_patterns = [
            r'TAXE:\s*([\d\s,]+)\s*FCFA',
            r'TAXES:\s*([\d\s,]+)\s*FCFA',
            r'TAXE\s*:\s*([\d\s,]+)\s*FCFA',
            r'TAX\s*:\s*([\d\s,]+)\s*FCFA',
            r'TVA:\s*([\d\s,]+)\s*FCFA',
            r'TIMBRE:\s*([\d\s,]+)\s*FCFA',
        ]

        for pattern in tax_patterns:
            matches = re.findall(pattern, normalized_upper)
            if matches:
                for match in matches:
                    tax_amount = parse_currency_amount(match)
                    if tax_amount and tax_amount > 0:
                        return tax_amount

        return None

    def extract_commission_only(self, normalized_body):
        """
        Extrait spécifiquement les commissions
        """
        normalized_upper = normalized_body.upper()
        commission_patterns = [
            r'COMMISSION:\s*([\d\s,]+)\s*FCFA',
            r'COMMISSION\s*:\s*([\d\s,]+)\s*FCFA',
            r'COMMISSION\s+([\d\s,]+)\s*FCFA',
            r'COMM\.:\s*([\d\s,]+)\s*FCFA',
        ]

        for pattern in commission_patterns:
            matches = re.findall(pattern, normalized_upper)
            if matches:
                for match in matches:
                    commission_amount = parse_currency_amount(match)
                    if commission_amount and commission_amount > 0:
                        return commission_amount

        return None