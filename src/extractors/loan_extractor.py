import re
from utils.helpers import parse_currency_amount

class LoanExtractor:
    
    def extract_total_due(self, normalized_body):
        """
        Extrait le montant total dû pour un prêt
        """
        patterns = [
            # Pattern spécifique Orange Bank
            r'NOUVEAU MONTANT A REMBOURSER:\s*([\d\s]+)\s*FCFA',
            r'MONTANT A REMBOURSER:\s*([\d\s]+)\s*FCFA',
            r'REMBOURSER:\s*([\d\s]+)\s*FCFA',
            r'RESTANT A REMBOURSER:\s*([\d\s]+)\s*FCFA',
            # Patterns pour le reste à rembourser
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