import re
import pandas as pd
from core.text_normalizer import normalize_sms
from core.currency_converter import currency_converter
from core.parsers import parse_currency_amount, normalize_date
from core.validators import is_valid_phone_number, is_valid_counterparty_name
from processors.multi_operation_processor import is_multi_operation_sms, process_multi_operation_sms
from classifiers.sms_classifier import extract_sms_type
from classifiers.label_classifier import extract_label
from classifiers.account_classifier import extract_account_type
from extractors.amount_extractor import extract_amount
from extractors.balance_extractor import extract_balance
from extractors.currency_extractor import extract_balance_currency
from extractors.currency_extractor import extract_currency
from extractors.counterparty_extractor import extract_counterparty_info
from extractors.date_extractor import extract_operation_date, extract_loan_deadline
from extractors.tax_extractor import extract_tax_and_fee
from extractors.loan_extractor import extract_loan_total_due
from extractors.reference_extractor import extract_reference
from utils.helpers import extract_client_id, extract_device_id, are_all_numeric_fields_null, should_ignore
from utils.logger import setup_logger

logger = setup_logger(__name__)

def process_single_operation_sms(row, normalized_body, original_body, s3_key, s3_bucket=None):
    """Traite un SMS avec une seule opération - VERSION SIMPLIFIÉE POUR LES PRÊTS (avec s3_key)"""

    # Extraction des informations de base
    tx_type = extract_sms_type(normalized_body)
    label = extract_label(normalized_body, tx_type)
    operation_date = extract_operation_date(normalized_body)

    # EXTRACTION DE LA DATE LIMITE pour les prêts
    loan_deadline = None
    if any(loan_word in normalized_body.upper() for loan_word in ['PRET', 'LOAN', 'ECHEANCE', 'REMBOURSEMENT', 'AVANT LE', 'JOURS AVANT']):
        loan_deadline = extract_loan_deadline(normalized_body, received_at=row['Received At'])

    # Extraction des données financières de base
    amt = extract_amount(normalized_body)
    balance_after = extract_balance(normalized_body)
    currency = extract_currency(normalized_body)
    loan_total_due = extract_loan_total_due(normalized_body)
    tax_and_fee = extract_tax_and_fee(normalized_body)

    # RÈGLE SPÉCIFIQUE POUR LES PRÊTS : Gestion de la contrepartie
    counterparty_name = None
    counterparty_phone = None

    if tx_type == 'LOAN':
        # RÈGLE : "Orange Bank" > "Orange Money" > None
        normalized_upper = normalized_body.upper()

        if "ORANGE BANK" in normalized_upper:
            counterparty_name = "Orange Bank"
        elif "ORANGE MONEY" in normalized_upper:
            counterparty_name = "Orange Money"
        else:
            counterparty_name = None

        # CAS SPÉCIFIQUES POUR LES DIFFÉRENTS TYPES DE PRÊTS
        if label in ['LOAN REPAYMENT REMINDER', 'OVERDUE LOAN REPAYMENT REMINDER']:
            if amt is None and loan_total_due is not None:
                pass  # Utilisation du montant dû déjà extrait

        # CAS SPÉCIFIQUE POUR LOAN DEFAULT WARNING
        elif label == 'LOAN DEFAULT WARNING':
            # FORCER amount = None car c'est une alerte, pas une transaction
            amt = None
            balance_after = None

        elif label in ['OVERDUE LOAN PARTIAL REPAYMENT', 'LOAN FULL REPAYMENT']:
            if amt is None:
                repayment_patterns = [
                    r'DEBITE DE\s+([\d\s]+)\s*FCFA',
                    r'REMBOURSE\s+([\d\s]+)\s*FCFA',
                    r'PARTIELLEMENT REMBOURSE.*?([\d\s]+)\s*FCFA'
                ]
                for pattern in repayment_patterns:
                    match = re.search(pattern, normalized_body, re.IGNORECASE)
                    if match:
                        amt = parse_currency_amount(match.group(1))
                        break

        elif label == 'LOAN DISBURSEMENT':
            if amt is None:
                net_pattern = r'MONTANT NET RECU\s*:\s*([\d\s]+)'
                match = re.search(net_pattern, normalized_body, re.IGNORECASE)
                if match:
                    amt = parse_currency_amount(match.group(1))

        elif label in ['LOAN ELIGIBILITY OFFER', 'SAVINGS-BASED LOAN OFFER']:
            if amt is None:
                pret_patterns = [
                    r'PRET DE\s+([\d\s]+)',
                    r'JUSQU[\'\s]*A\s+([\d\s]+)',
                    r'RECEVEZ\s+JUSQU[\'\s]*A\s+([\d\s]+)'
                ]
                for pattern in pret_patterns:
                    match = re.search(pattern, normalized_body, re.IGNORECASE)
                    if match:
                        amt = parse_currency_amount(match.group(1))
                        break

    else:
        # Pour les autres types de messages, utilisation de l'extraction normale
        counterparty_name, counterparty_phone = extract_counterparty_info(normalized_body, tx_type)

    # Gestion de la devise
    amount_currency = extract_currency(normalized_body)
    balance_currency = extract_balance_currency(normalized_body)

    # Détermination de la devise finale
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

    # Conversion automatique si nécessaire
    if needs_conversion:
        converted_amount = currency_converter.convert_amount(amt, amount_currency, balance_currency)
        if converted_amount != amt:
            amt = converted_amount

    # Vérifier si tous les champs numériques sont nuls
    if are_all_numeric_fields_null(amt, balance_after, None, tax_and_fee, loan_total_due):
        return []

    return [create_transaction_record(
        row, normalized_body, tx_type, counterparty_name, counterparty_phone,
        amt, label, balance_after, final_currency, original_body, operation_date,
        loan_deadline, s3_key, s3_bucket  # ← Maintenant s3_bucket est disponible
    )]

def create_transaction_record(row, normalized_body, tx_type, counterparty_name, counterparty_phone,
                            amt, label, balance_after, currency, original_body, operation_date=None,
                            loan_deadline=None, s3_key=None, s3_bucket=None):
    
    account_type = extract_account_type(row, normalized_body, tx_type, label)
    tax_and_fee = extract_tax_and_fee(normalized_body)
    loan_total_due = extract_loan_total_due(normalized_body)
    if operation_date is None:
        operation_date = extract_operation_date(normalized_body)
    
    from utils.helpers import extract_client_id, extract_device_id
    client_id = extract_client_id(s3_key)
    device_id = extract_device_id(s3_key)

    return {
        'message_id': row.get('Message ID', ''),
        'client_id': client_id,
        'device_id': device_id,
        'service_name': row.get('Sender ID', ''),
        'counterparty_name': counterparty_name,
        'counterparty_phone': counterparty_phone,
        'account_type': account_type,
        'message_type': tx_type,
        'amount': amt,
        'label': label,
        'balance_after': balance_after,
        'tax_and_fee': tax_and_fee,
        'loan_total_due': loan_total_due,
        'loan_deadline': loan_deadline,
        'currency': currency,
        'provider_ref': extract_reference(normalized_body),
        'event_time': row.get('Received At', ''),
        'operation_date': operation_date,
        'data_source': f"s3://{s3_bucket}/{s3_key}",
        'path': s3_key
    }

def process_sms(row, s3_key, s3_bucket=None):

    
    if should_ignore(row):
        return []

    original_body = str(row['Body'])
    normalized_body = normalize_sms(original_body)

    # Vérifier si c'est un SMS multi-opérations
    if is_multi_operation_sms(normalized_body):
        return process_multi_operation_sms(row, normalized_body, original_body, s3_key, s3_bucket)

    return process_single_operation_sms(row, normalized_body, original_body, s3_key, s3_bucket)