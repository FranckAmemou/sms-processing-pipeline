# src/extractors/__init__.py

# Import flexible avec gestion des noms de fonctions différents
from .amount_extractor import extract_amount
from .balance_extractor import extract_balance
from .counterparty_extractor import extract_counterparty_info as extract_counterparty
from .currency_extractor import extract_currency
from .date_extractor import extract_operation_date as extract_date
from .reference_extractor import extract_reference
from .tax_extractor import extract_tax_and_fee as extract_tax

__all__ = [
    'extract_amount',
    'extract_balance', 
    'extract_counterparty',
    'extract_currency',
    'extract_date',
    'extract_reference',
    'extract_tax'
]