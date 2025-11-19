import re
def extract_account_type(row, normalized_body, transaction_type, label):
    """

    """
    normalized_upper = normalized_body.upper()

# ACCÈS DIRECT au Sender ID depuis la row du CSV
    sender_name = str(row.get('Sender ID', '')).upper()


#  VÉRIFICATION COMPTE ÉPARGNE (SAVINGS ACCOUNT)
    savings_indicators = [
        'LE SOLDE DE VOTRE EPARGNE',
        'COMPTE EPARGNE A ETE DEBITE',  #  AJOUTER VIRGULE ICI
        'SOLDE EPARGNE',
        'VOTRE EPARGNE A ETE DEBITE'   #  AJOUTER VIRGULE ICI (dernier élément optionnel)
    ]

    for phrase in savings_indicators:
        if phrase in normalized_upper:

            return "SAVINGS ACCOUNT"

#  VÉRIFICATION COMPTE MOBILE (MOBILE ACCOUNT)
    mobile_money_senders = [
        'ORANGEMONEY', 'ORANGE MONEY', 'ORANGE-MONEY', 'ORANGEMONY',
        'MOOV MONEY', 'MOOVMONEY', 'MOOV',
        'MTN MONEY', 'MTNMONEY', 'MTN MOMO', 'MTN',
        'FLOOZ', 'FLOOZ CI', 'FLOOZCI','INFO ORANGE',
        'TIKTAK', 'WAVE', 'YUP', 'CINAR', 'JONA',
        '2SICASH', '2SI CASH', 'ECOBANK MOMO', 'ECOBANK-MOMO','TIK TAK'
    ]

# Vérification par EXPÉDITEUR (Sender ID)
    if sender_name and sender_name not in ['', 'NAN', 'NONE', 'NONE']:
        for sender in mobile_money_senders:
            if sender in sender_name:

                return "MOBILE ACCOUNT"

# Vérification par CONTENU du SMS (fallback)
    mobile_money_content = [
        'COMPTE OM', 'ORANGE MONEY', 'SOLDE OM',
        'MOOV MONEY', 'SOLDE MOOV', 'FLOOZ',
        'MTN MOMO', 'MTN MONEY', 'MOBILE MONEY',
        'COMPTE PRINCIPAL MOOV MONEY', 'WAVE',
        'PORTEFEUILLE ELECTRONIQUE', 'TIKTAK',
        'YUP', 'CINAR', 'JONA', '2SICASH',
        'VIA OM', 'PAR OM', 'COMPTE OM', 'SOLDE ORANGE MONEY'
    ]

    for phrase in mobile_money_content:
        if phrase in normalized_upper:

            return "MOBILE ACCOUNT"

# COMPTE COURANT (CURRENT ACCOUNT) - PAR DÉFAUT

    return "CURRENT ACCOUNT"