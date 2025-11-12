import re
from datetime import datetime



# ✅ NOUVEAU (imports absolus)
from core.text_normalizer import normalize_sms
from classifiers.sms_classifier import SMSClassifier
from classifiers.label_classifier import LabelClassifier
from classifiers.account_classifier import AccountClassifier
from extractors.amount_extractor import AmountExtractor
from extractors.balance_extractor import BalanceExtractor
from extractors.counterparty_extractor import CounterpartyExtractor
from extractors.date_extractor import DateExtractor
from extractors.tax_extractor import TaxExtractor
from extractors.loan_extractor import LoanExtractor
from extractors.reference_extractor import ReferenceExtractor
from extractors.currency_extractor import CurrencyExtractor
from config.services import SERVICE_NAME_USED, IGNORE_KEYWORDS
from utils.helpers import are_all_numeric_fields_null, extract_client_id, extract_device_id
from core.currency_converter import currency_converter
from processors.multi_operation_processor import MultiOperationProcessor

class SMSProcessor:
    def __init__(self):
        self.sms_classifier = SMSClassifier()
        self.label_classifier = LabelClassifier()
        self.account_classifier = AccountClassifier()
        self.amount_extractor = AmountExtractor()
        self.balance_extractor = BalanceExtractor()
        self.counterparty_extractor = CounterpartyExtractor()
        self.date_extractor = DateExtractor()
        self.tax_extractor = TaxExtractor()
        self.loan_extractor = LoanExtractor()  
        self.reference_extractor = ReferenceExtractor()
        self.currency_extractor = CurrencyExtractor() 
        self.multi_operation_processor = MultiOperationProcessor()
    
    def should_ignore(self, row):
        """Vérifie si un SMS doit être ignoré - VERSION OPTIMISÉE"""
        sender = str(row.get('Sender ID', ''))
        body = str(row.get('Body', '')).lower()
        body_normalized = body.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('à', 'a')

        if sender not in SERVICE_NAME_USED:
            return True

        is_orange_bank_epargne_gelee = (
            'orange bank' in body_normalized and
            'epargne geles' in body_normalized and
            'pret' in body_normalized
        )

        if is_orange_bank_epargne_gelee:
            return False

        is_pure_balance_message = (
            'solde de vos comptes' in body_normalized and
            'compte principal:' in body_normalized and
            'compte salaire:' in body_normalized and
            not any(transaction_word in body_normalized for transaction_word in [
                'debite', 'credite', 'recu', 'envoye', 'paye', 'achete',
                'retrait', 'depot', 'virement', 'transaction'
            ])
        )

        if is_pure_balance_message:
            return True

        if 'PUSH CI' in sender and 'coffre' in body and 'virement' in body:
            return False

        is_mtn_momo_payment = (
            'momo' in body_normalized and
            ('paiement' in body_normalized or 'debit' in body_normalized) and
            any(phrase in body_normalized for phrase in ['effectue', 'succes']) and
            ('mtn' in body_normalized or 'mobile money' in body_normalized)
        )

        if is_mtn_momo_payment:
            return False

        is_mobile_money_transaction = any(keyword in body for keyword in [
            'mobile money', 'orange money', 'mtn money', 'moov money', 'wave', 'flooz'
        ]) and any(action in body for action in [
            'vous avez recu', 'vous avez envoye', 'transfert recu', 'transfert envoye',
            'transfert international recu', 'recu', 'expediteur'
        ]) and not any(ignore_word in body for ignore_word in [
            'code de retrait', 'expire dans', 'veuillez utiliser','en cours.'
        ])

        if is_mobile_money_transaction:
            return False

        is_wave_transaction = (
            'wave' in body_normalized and
            any(keyword in body_normalized for keyword in [
                'transfere', 'transfert', 'recu', 'envoye', 'solde wave'
            ])
        )

        if is_wave_transaction:
            return False

        is_debit_carte = (
            'debit carte' in body_normalized and
            any(keyword in body_normalized for keyword in [
                'montant', 'solde', 'date operation', 'ref'
            ])
        )

        if is_debit_carte:
            return False

        if any(k.lower() in body for k in IGNORE_KEYWORDS):
            return True

        return False
    
    def is_multi_operation_sms(self, normalized_body):
        """Détecte si le SMS contient plusieurs opérations"""
        multi_op_indicators = [
            r'COMPTE\s+\d+.*EN FCFA\s*:.*\d{1,2}/\d{1,2}\s+-\d+',
            r'\d{1,2}/\d{1,2}\s+-\d+\s+[A-Z].*\d{1,2}/\d{1,2}\s+-\d+',
            r'(\d{1,2}/\d{1,2}\s+-\d+\s+[A-Z][^\.]*){2,}',
            r'MINI-RELEVE COMPTE.*\d{1,3}\.\d{3} XOF',
            r'MINI RELEVE COMPTE.*\d{1,3}\.\d{3} XOF',
            r'MINI-RELEVE COMPTE',
            r'MINI RELEVE COMPTE',
            r'MINI RELEVE ARRETE DE CPTE AU',
            r'MINI-RELEVE ARRETE DE CPTE AU',
            r'ARRETE DE CPTE AU.*\d{2}/\d{2}/\d{4}.*XOF.*ARRETE DE CPTE AU',
            r'(ARRETE DE CPTE AU[^.]*\.){2,}',
            r'\d{2}/\d{2}/\d{4},-?\d+XOF.*\d{2}/\d{2}/\d{4},-?\d+XOF',
            r'MINI RELEVE.*VIREMENT RECU DE.*\d{2}/\d{2}/\d{4},[+-]\d+XOF',
            r'MINI RELEVE.*SGCNCT.*\d{2}/\d{2}/\d{4},[+-]\d+XOF',
            r'(?:[A-Z][A-Z0-9\s]+,)?\d{2}/\d{2}/\d{4},[+-]\d+XOF\.\s*(?:[A-Z][A-Z0-9\s]+,)?\d{2}/\d{2}/\d{4},[+-]\d+XOF'
        ]

        return any(re.search(pattern, normalized_body, re.IGNORECASE) for pattern in multi_op_indicators)
    
    def create_transaction_record(self, row, normalized_body, tx_type, counterparty_name, counterparty_phone,
                                amt, label, balance_after, currency, original_body, s3_key, operation_date=None):
        """Crée un enregistrement de transaction standardisé"""
        account_type = self.account_classifier.classify(row, normalized_body, tx_type, label)
        
        if operation_date is None:
            operation_date = self.date_extractor.extract_operation_date(normalized_body)

        tax_and_fee = self.tax_extractor.extract(normalized_body)
        loan_total_due = self.loan_extractor.extract_total_due(normalized_body) 
        provider_ref = self.reference_extractor.extract(normalized_body)

        return {
            'message_id': row['Message ID'],
            'client_id': extract_client_id(s3_key),
            'device_id': extract_device_id(s3_key),
            'service_name': row['Sender ID'],
            'counterparty_name': counterparty_name,
            'counterparty_phone': counterparty_phone,
            'account_type': account_type,
            'message_type': tx_type,
            'amount': amt,
            'label': label,
            'balance_after': balance_after,
            'tax_and_fee': tax_and_fee,
            'loan_total_due': loan_total_due,
            'currency': currency,
            'provider_ref': provider_ref,
            'event_time': row['Received At'],
            'operation_date': operation_date,
            'data_source': f"s3://{s3_key}",
            'processed_at': datetime.now().isoformat()
        }
    
    def process_sms(self, row, s3_key):
        """Traite un SMS individuel"""
        original_body = str(row['Body'])
        normalized_body = normalize_sms(original_body)

        if self.is_multi_operation_sms(normalized_body):
            return self.process_multi_operation_sms(row, normalized_body, original_body, s3_key)
        else:
            return self.process_single_operation_sms(row, normalized_body, original_body, s3_key)
    
    def process_single_operation_sms(self, row, normalized_body, original_body, s3_key):
        """Traite un SMS avec une seule opération"""
        tx_type = self.sms_classifier.classify(normalized_body)
        counterparty_name, counterparty_phone = self.counterparty_extractor.extract(normalized_body, tx_type)
        amt = self.amount_extractor.extract(normalized_body)
        label = self.label_classifier.classify(normalized_body, tx_type)
        balance_after = self.balance_extractor.extract(normalized_body)
        operation_date = self.date_extractor.extract_operation_date(normalized_body)

        amount_currency = self.currency_extractor.extract_currency(normalized_body)
        balance_currency = self.currency_extractor.extract_balance_currency(normalized_body)

        if balance_currency is not None:
            final_currency = balance_currency
            needs_conversion = (amt is not None and amount_currency != balance_currency)
        elif balance_after is not None and amount_currency is not None:
            final_currency = amount_currency
            needs_conversion = False
        elif amt is not None and amount_currency is not None:
            final_currency = amount_currency
            needs_conversion = False
        else:
            final_currency = 'XOF'
            needs_conversion = False

        if needs_conversion:
            converted_amount = currency_converter.convert_amount(amt, amount_currency, balance_currency)
            if converted_amount != amt:
                amt = converted_amount

        tax_and_fee = self.tax_extractor.extract(normalized_body)
        loan_interest = None
        loan_total_due = self.loan_extractor.extract_total_due(normalized_body)

        if are_all_numeric_fields_null(amt, balance_after, loan_interest, tax_and_fee, loan_total_due):
            return []

        return [self.create_transaction_record(
            row, normalized_body, tx_type, counterparty_name, counterparty_phone,
            amt, label, balance_after, final_currency, original_body, s3_key, operation_date
        )]
    
    def process_multi_operation_sms(self, row, normalized_body, original_body, s3_key):
        """Traite un SMS multi-opérations"""
        operations = self.multi_operation_processor.extract_multi_operation_details(normalized_body)
        transactions = []

        for op in operations:
            if op['amount'] > 0:
                tx_type = 'CREDIT'
            else:
                tx_type = 'DEBIT'

            transaction = self.create_transaction_record(
                row, normalized_body,
                tx_type,
                None, None,
                op['amount'],
                op['label'],
                None,
                'XOF',
                original_body,
                s3_key,
                operation_date=op['date']
            )
            transactions.append(transaction)

        return transactions