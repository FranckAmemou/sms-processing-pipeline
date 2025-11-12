import re
from utils.logger import setup_logger
from utils.helpers import parse_currency_amount

class MultiOperationProcessor:
    
    def extract_multi_operation_details(self, normalized_body):
        """Extrait les détails des SMS multi-opérations - VERSION COMPLÈTE OPTIMISÉE"""
        operations = []

        # 1. DÉTECTION FORMAT MIXTE AVEC DESCRIPTIONS DÉTAILLÉES
        if "MINI RELEVE" in normalized_body:
            # Pattern principal pour extraire: [DESCRIPTION],[DATE],[+/-MONTANT]XOF
            pattern = r'([A-Z][A-Z0-9\s\-\/]+),(\d{2}/\d{2}/\d{4}),([+-]?\d+)XOF'
            matches = re.findall(pattern, normalized_body)

            for description, date_str, amount_str in matches:
                try:
                    amount = parse_currency_amount(amount_str)
                    description_clean = description.strip()
                    description_upper = description_clean.upper()

                    # DÉFINITION DES CATÉGORIES DE MOTS-CLÉS
                    bank_fees_keywords = ['ARRETE DE CPTE', 'FACTURATION', 'FACT PACK', 'COTISATION',
                                        'PACK', 'AGIOS', 'COMMISSION', 'FRAIS', 'COTISATION CARTE', 'FACTURATION CONNECT']

                    transfer_keywords = ['VIREMENT RECU', 'SGCNCT', 'VIR FAV', 'VIR AUTRE', 'VIR AUTRE BQE', 'VIREMENTS RECUS']
                    subscription_keywords = ['MESSALIA', 'ABONNEMENT', 'PUSH HEBDO', 'PUSH HEBDO EV', 'PUSH HEBDO SIMPLE']
                    withdrawal_keywords = ['RETRAIT', 'WITHDRAWAL', 'RETRAIT DAB', 'RETRAIT GUICHET']
                    deposit_keywords = ['DEPOT', 'VERSEMENT', 'VERSEMENT ESPECE', 'VERSEMENT EFFECTUE']
                    insurance_keywords = ['ASSURANCE', 'ASSURANCE VIE', 'SECURICOMP', 'ASS-PARRAINAGE', 'ACP', 'NSIA VIE']
                    tax_keywords = ['TAXE', 'PRELEVEMENT', 'LIBERATOI', 'PRELEVEMENT LIBERATOI']
                    salary_keywords = ['SALAIRE', 'SALARY']
                    loan_keywords = ['PRET', 'LOAN', 'EMPRUNT', 'ECHEANCE', 'MENSUALITE', 'REMBOURSEMENT']
                    interest_keywords = ['INTERET', 'INTEREST']
                    purchase_keywords = ['PAIEMENT', 'ACHAT', 'PMT', 'ACHAT TPE', 'TPE/ONLINE']
                    education_keywords = ['PLAN EDUCATION', 'EDUCATION', 'SOGETUDES']

                    # DÉTERMINATION INTELLIGENTE DES LABELS
                    label = "BANK OPERATION"

                    if any(word in description_upper for word in bank_fees_keywords):
                        label = "BANK FEES"
                    elif any(word in description_upper for word in transfer_keywords):
                        if amount > 0:
                            label = "INCOMING TRANSFER"
                        else:
                            label = "OUTGOING TRANSFER"
                    elif any(word in description_upper for word in subscription_keywords):
                        label = "SUBSCRIPTION"
                    elif any(word in description_upper for word in withdrawal_keywords):
                        label = "CASH WITHDRAWAL"
                    elif any(word in description_upper for word in deposit_keywords) and amount > 0:
                        label = "CASH DEPOSIT"
                    elif any(word in description_upper for word in insurance_keywords):
                        label = "INSURANCE PAYMENT"
                    elif any(word in description_upper for word in tax_keywords):
                        label = "TAX PAYMENT"
                    elif any(word in description_upper for word in salary_keywords):
                        label = "SALARY"
                    elif any(word in description_upper for word in loan_keywords):
                        label = "LOAN REPAYMENT"
                    elif any(word in description_upper for word in interest_keywords):
                        if amount > 0:
                            label = "INTEREST INCOME"
                        else:
                            label = "INTEREST PAYMENT"
                    elif any(word in description_upper for word in purchase_keywords):
                        label = "PURCHASE"
                    elif any(word in description_upper for word in education_keywords):
                        label = "EDUCATION SAVINGS"
                    else:
                        if amount > 0:
                            label = "INCOMING TRANSFER"
                        else:
                            label = "BANK OPERATION"

                    operations.append({
                        'date': date_str,
                        'amount': amount,
                        'description': description_clean,
                        'label': label
                    })

                except Exception as e:
                    continue

        # DÉTECTION FORMAT "ARRETE DE CPTE AU" SPÉCIFIQUE
        if "ARRETE DE CPTE AU" in normalized_body and not operations:
            pattern = r'ARRETE DE CPTE AU,(\d{2}/\d{2}/\d{4}),(-?\d+)XOF'
            matches = re.findall(pattern, normalized_body)

            for date_str, amount_str in matches:
                try:
                    amount = parse_currency_amount(amount_str)
                    operations.append({
                        'date': date_str,
                        'amount': amount,
                        'description': f"ARRETE DE CPTE AU {date_str}",
                        'label': "BANK FEES"
                    })
                except Exception:
                    continue

        # DÉTECTION MINI-RELEVÉS STANDARDS
        if ("MINI-RELEVE COMPTE" in normalized_body or "MINI RELEVE COMPTE" in normalized_body) and not operations:
            mini_releve_patterns = [
                r'([+-]?\d{1,3}(?:\.\d{3})*)\s*XOF\s*DU\s*(\d{2}/\d{2}/\d{2,4})',
                r'([+-]?\d+)\s*XOF\s*DU\s*(\d{2}/\d{2}/\d{2,4})',
                r'([+-]?[\d\.,]+)\s*XOF\s*DU\s*(\d{1,2}/\d{1,2}/\d{2,4})'
            ]

            matches = []
            for pattern in mini_releve_patterns:
                pattern_matches = re.findall(pattern, normalized_body)
                if pattern_matches:
                    matches.extend(pattern_matches)
                    break

            for amount_str, date_str in matches:
                try:
                    amount_clean = amount_str.replace('.', '').replace(',', '')
                    amount = parse_currency_amount(amount_clean)

                    date_parts = date_str.split('/')
                    if len(date_parts) >= 2:
                        short_date = f"{date_parts[0]}/{date_parts[1]}"
                    else:
                        short_date = date_str

                    operations.append({
                        'date': short_date,
                        'amount': amount,
                        'description': f"MINI-RELEVE {date_str}",
                        'label': "BANK OPERATION"
                    })
                except Exception:
                    continue

        # DÉTECTION OPÉRATIONS MULTIPLES CLASSIQUES
        if not operations:
            operation_pattern = r'(\d{1,2}/\d{1,2})\s+([+-]\d+(?:\.\d+)?)\s+([A-Z0-9][^-+]*?)(?=\s+\d{1,2}/\d{1,2}\s+[+-]\d+|$)'
            matches = re.findall(operation_pattern, normalized_body)

            for date, amount_str, description in matches:
                amount = parse_currency_amount(amount_str)
                description_clean = description.strip()
                description_upper = description_clean.upper()

                bank_fees_keywords = ['PACK', 'AGIOS', 'COMMISSION', 'FRAIS', 'COTISATION',
                                    'ABONNEMENT', 'COTISATION CARTE', 'ARRETE DE CPTE',
                                    'FACT PACK', 'FACTURATION']

                transfer_keywords = ['VIREMENT SIB RECU', 'VIREMENT SIB VERS', 'VIREMENT RECU',
                                   'SGCNCT', 'VIR FAV', 'VIR AUTRE']

                subscription_keywords = ['MESSALIA', 'PUSH HEBDO']
                withdrawal_keywords = ['RETRAIT', 'RETIRE', 'RETRAIT DAB', 'RETRAIT GUICHET']
                deposit_keywords = ['VERSEMENT ESPECE', 'DEPOT', 'VERSEMENT EFFECTUE']
                insurance_keywords = ['ASSURANCE', 'ASS ', 'SECURICOMP', 'ASS-PARRAINAGE', 'ACP']
                tax_keywords = ['PRELEVEMENT LIBERATOI', 'TAXE']
                education_keywords = ['PLAN EDUCATION', 'EDUCATION', 'SOGETUDES']
                purchase_keywords = ['PAIEMENT', 'ACHAT', 'PMT']

                label = "BANK OPERATION"

                if any(word in description_upper for word in bank_fees_keywords):
                    label = "BANK FEES"
                elif any(word in description_upper for word in transfer_keywords):
                    if amount > 0:
                        label = "INCOMING TRANSFER"
                    else:
                        label = "OUTGOING TRANSFER"
                elif any(word in description_upper for word in subscription_keywords):
                    label = "SUBSCRIPTION"
                elif any(word in description_upper for word in withdrawal_keywords):
                    label = "CASH WITHDRAWAL"
                elif any(word in description_upper for word in deposit_keywords) and amount > 0:
                    label = "CASH DEPOSIT"
                elif any(word in description_upper for word in insurance_keywords):
                    label = "INSURANCE PAYMENT"
                elif any(word in description_upper for word in tax_keywords):
                    label = "TAX PAYMENT"
                elif any(word in description_upper for word in education_keywords):
                    label = "EDUCATION SAVINGS"
                elif any(word in description_upper for word in purchase_keywords):
                    label = "PURCHASE"
                else:
                    label = "BANK OPERATION"

                operations.append({
                    'date': date,
                    'amount': amount,
                    'description': description_clean,
                    'label': label
                })

        return operations