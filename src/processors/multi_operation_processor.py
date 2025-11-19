import re
from utils.logger import setup_logger
import pandas as pd
from core.text_normalizer import normalize_sms
from core.parsers import parse_currency_amount
from sms_processor import create_transaction_record
from utils.helpers import extract_client_id, extract_device_id

def is_multi_operation_sms(normalized_body):
    """Détecte si le SMS contient plusieurs opérations - VERSION ÉTENDUE"""
    multi_op_indicators = [
        # Pattern pour "COMPTE XXXX EN FCFA : date1 -montant1 description1 date2 -montant2 description2"
        r'COMPTE\s+\d+.*EN FCFA\s*:.*\d{1,2}/\d{1,2}\s+-\d+',
        r'\d{1,2}/\d{1,2}\s+-\d+\s+[A-Z].*\d{1,2}/\d{1,2}\s+-\d+',
        # Pattern pour plusieurs opérations consécutives
        r'(\d{1,2}/\d{1,2}\s+-\d+\s+[A-Z][^\.]*){2,}',

        #  Patterns pour mini-relevés (FORMATS SOCIÉTÉ GÉNÉRALE)
        r'MINI-RELEVE COMPTE.*\d{1,3}\.\d{3} XOF',
        r'MINI RELEVE COMPTE.*\d{1,3}\.\d{3} XOF',
        r'MINI-RELEVE COMPTE',
        r'MINI RELEVE COMPTE',

        #  Pattern spécifique pour "MINI RELEVE ARRETE DE CPTE AU"
        r'MINI RELEVE ARRETE DE CPTE AU',
        r'MINI-RELEVE ARRETE DE CPTE AU',
        r'MINI RELEVE.*ARRETE DE CPTE',
        r'MINI-RELEVE.*ARRETE DE CPTE',

        # Pattern pour détecter plusieurs "ARRETE DE CPTE AU" consécutifs
        r'ARRETE DE CPTE AU.*\d{2}/\d{2}/\d{4}.*XOF.*ARRETE DE CPTE AU',
        r'(ARRETE DE CPTE AU[^.]*\.){2,}',

        #  Pattern pour détecter plusieurs dates avec montants XOF
        r'\d{2}/\d{2}/\d{4},-?\d+XOF.*\d{2}/\d{2}/\d{4},-?\d+XOF',

        #  Pattern pour le format mixte avec VIREMENT RECU et autres opérations
        r'MINI RELEVE.*VIREMENT RECU DE.*\d{2}/\d{2}/\d{4},[+-]\d+XOF',
        r'MINI RELEVE.*SGCNCT.*\d{2}/\d{2}/\d{4},[+-]\d+XOF',
        r'MINI RELEVE.*ARRETE DE CPTE AU.*\d{2}/\d{2}/\d{4},[+-]\d+XOF',

        #  Pattern général pour mini-relevés avec opérations variées
        r'(?:[A-Z][A-Z0-9\s]+,)?\d{2}/\d{2}/\d{4},[+-]\d+XOF\.\s*(?:[A-Z][A-Z0-9\s]+,)?\d{2}/\d{2}/\d{4},[+-]\d+XOF'
    ]

    return any(re.search(pattern, normalized_body, re.IGNORECASE) for pattern in multi_op_indicators)
def process_multi_operation_sms(row, normalized_body, original_body,s3_key, s3_bucket):
    """Traite un SMS contenant plusieurs opérations"""
    operations = extract_multi_operation_details(normalized_body)
    transactions = []

    for op in operations:
        # Déterminer le type de message basé sur le montant
        if op['amount'] > 0:
            tx_type = 'CREDIT'
        else:
            tx_type = 'DEBIT'

        transaction = create_transaction_record(
            row, normalized_body,
            tx_type,
            None, None,
            op['amount'],
            op['label'],
            None,
            'XOF',
            original_body,  # ↑ Toujours passé mais non utilisé
            operation_date=op['date'],
            s3_key=s3_key,  # ← Ajouter ces paramètres
            s3_bucket=s3_bucket
        )
        transactions.append(transaction)

    return transactions
def extract_multi_operation_details(normalized_body):
    """Extrait les détails des SMS multi-opérations - VERSION COMPLÈTE OPTIMISÉE"""

    operations = []
    # print(f"[DEBUG] Début extraction multi-opérations: {normalized_body}")

    #  1. DÉTECTION FORMAT MIXTE AVEC DESCRIPTIONS DÉTAILLÉES
    if "MINI RELEVE" in normalized_body:


        # Pattern principal pour extraire: [DESCRIPTION],[DATE],[+/-MONTANT]XOF
        pattern = r'([A-Z][A-Z0-9\s\-\/]+),(\d{2}/\d{2}/\d{4}),([+-]?\d+)XOF'
        matches = re.findall(pattern, normalized_body)

        # print(f"[DEBUG] Matches trouvés avec pattern principal: {matches}")

        for description, date_str, amount_str in matches:
            try:
                amount = parse_currency_amount(amount_str)
                description_clean = description.strip()
                description_upper = description_clean.upper()

                #  DÉFINITION DES CATÉGORIES DE MOTS-CLÉS
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
                label = "BANK OPERATION"  # Valeur par défaut

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
                    # Fallback basé sur le montant
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

        # Si on a trouvé des opérations avec le pattern principal, on retourne
        if operations:

            return operations

    #  DÉTECTION FORMAT "ARRETE DE CPTE AU" SPÉCIFIQUE (fallback)
    if "ARRETE DE CPTE AU" in normalized_body:


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

                # print(f"[DEBUG] Opération spécifique ajoutée: {date_str} {amount} BANK FEES")

            except Exception as e:
                # print(f"[DEBUG] Erreur traitement opération spécifique {amount_str} {date_str}: {e}")
                continue

    # DÉTECTION MINI-RELEVÉS STANDARDS (autres formats)
    if "MINI-RELEVE COMPTE" in normalized_body or "MINI RELEVE COMPTE" in normalized_body:


        # Patterns pour mini-relevés standards
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

        # Secours : extraction manuelle si nécessaire
        if not matches:
            # print("[DEBUG] Aucun pattern standard ne fonctionne, tentative d'extraction manuelle...")

            manual_pattern = r'([+-]?[\d\.,]+)\s*XOF\s*DU\s*[\d/]+'
            manual_matches = re.findall(manual_pattern, normalized_body)


            date_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4})'
            dates = re.findall(date_pattern, normalized_body)


            for i, amount_str in enumerate(manual_matches):
                if i < len(dates):
                    matches.append((amount_str, dates[i]))



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



            except Exception as e:

                continue

    #  4. DÉTECTION OPÉRATIONS MULTIPLES CLASSIQUES (format historique)
    if not operations:
        # print(f"[DEBUG] Tentative avec pattern classique: {normalized_body}")
        operation_pattern = r'(\d{1,2}/\d{1,2})\s+([+-]\d+(?:\.\d+)?)\s+([A-Z0-9][^-+]*?)(?=\s+\d{1,2}/\d{1,2}\s+[+-]\d+|$)'
        matches = re.findall(operation_pattern, normalized_body)

        # print(f"[DEBUG] Pattern classique - Matches trouvés: {matches}")

        for date, amount_str, description in matches:
            amount = parse_currency_amount(amount_str)
            description_clean = description.strip()
            description_upper = description_clean.upper()

            # RÉUTILISATION DES MÊMES CATÉGORIES POUR LE FORMAT CLASSIQUE
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

            # DÉTERMINATION DU LABEL AVEC if any(...)
            label = "BANK OPERATION"  # Valeur par défaut

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


