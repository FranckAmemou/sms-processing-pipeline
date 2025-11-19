
# Constantes globales
DEFAULT_CURRENCY = 'XOF'
SUPPORTED_CURRENCIES = ['XOF', 'USD', 'EUR', 'FCFA']

# Patterns regex communs
PHONE_PATTERNS = [
    r'(\d{8,15})',
    r'(\d{2}\s\d{2}\s\d{2}\s\d{2})'
]

DATE_PATTERNS = [
    r'(\d{2}-\d{2}-\d{4})',
    r'(\d{2}/\d{2}/\d{4})',
    r'(\d{4}-\d{2}-\d{2})'
]