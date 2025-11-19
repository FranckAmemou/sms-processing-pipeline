import re

from core.parsers import parse_currency_amount

def extract_balance(normalized_body):
    """Extrait le solde du message SMS - VERSION QUI GARDE L'EXISTANT"""

    #  Patterns spécifiques UNIQUEMENT pour le cas problématique
    specific_patterns = [
        # Patterns EXTRÊMEMENT spécifiques pour "Nouveau solde OM : 678934.5 FCFA"
        r'NOUVEAU SOLDE OM\s*:\s*(\d+)\.(\d+)\s*FCFA',
        r'SOLDE OM\s*:\s*(\d+)\.(\d+)\s*FCFA',
    ]

    for pattern in specific_patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            integer_part = match.group(1)
            decimal_part = match.group(2)
            amount_float = parse_currency_amount(f"{integer_part}.{decimal_part}")

            return amount_float

    # L'EXISTANT SANS MODIFICATION
    patterns = [
                #NOUVEAUX PATTERNS pour solde Orange Money
        r'SOLDE ORANGE MONEY\s*:\s*([\d\s,]+)\s*F',
        r'SOLDE ORANGE MONEY\s*:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE OM\s*:\s*([\d\s,]+)\s*F',
          # Pattern pour Wave "Solde Wave: 113.143F"
        r'SOLDE WAVE:\s*(\d+\.\d+)F',
        r'SOLDE WAVE\s*:\s*(\d+\.\d+)F',
        r'WAVE:\s*(\d+\.\d+)F',
        # Patterns Orange Money (EXISTANT)
        r'NOUVEAU SOLDE OM\s*:\s*([\d\.,]+)\s*FCFA',
        r'SOLDE OM\s*:\s*([\d\.,]+)\s*FCFA',
        r'NOUVEAU SOLDE ORANGE MONEY\s*:\s*([\d\.,]+)\s*FCFA',
        r'SOLDE ORANGE MONEY\s*:\s*([\d\.,]+)\s*FCFA',

                # Pattern spécifique Orange Money "Solde compte intraregional: X FCFA"
        r'SOLDE COMPTE INTRAREGIONAL[:\s]*([\d\s]+)\s*FCFA',
        r'COMPTE INTRAREGIONAL[:\s]*([\d\s,]+)\s*FCFA',
        r'SOLDE COMPTE[:\s]*([\d\s]+)\s*FCFA',
                # Pattern pour "Votre solde est de 26.090,00"
        r'VOTRE SOLDE EST DE\s+([\d\.,]+)',
        r'SOLDE EST DE\s+([\d\.,]+)',
        r'VOTRE SOLDE\s+([\d\.,]+)',
        r'SOLDE\s+([\d\.,]+)',
        r'SOLDE:\s*([\d\.,]+)',
        r'NEW BALANCE[^\d]*([\d\.,]+)',
        r'NOUVEAU SOLDE[^\d]*([\d\.,]+)'
        # Pattern pour "Votre solde est de -7.778,00"
        r'VOTRE SOLDE EST DE\s+([-]\s*[\d\.,]+)',
        r'SOLDE EST DE\s+([-]\s*[\d\.,]+)',
        r'VOTRE SOLDE\s+([-]\s*[\d\.,]+)',
        r'SOLDE\s+([-]\s*[\d\.,]+)',
        r'SOLDE:\s*([-]\s*[\d\.,]+)',
        # Pattern général avec signe négatif
        r'SOLDE[^\d]*-([\d\.,]+)',
        r'BALANCE[^\d]*-([\d\.,]+)'
        r'NOUVEAU SOLDE:\s*([\d\.,]+)F',
        r'NOUVEAU SOLDE\s*:\s*([\d\.,]+)F',
        r'SOLDE:\s*([\d\.,]+)F',
        r'NEW BALANCE:\s*([\d\.,]+)F'
                # NOUVEAU : Pattern pour solde TresorMoney
        r'SOLDE:\s*([\d\s]+)(?=\s*$|\.)',
        r'SOLDE:\s*([\d\s,]+)',
        #Patterns pour soldes avec USD
        r'VOTRE NOUVEAU SOLDE EST DE\s+([\d\s,\.]+)\s*XOF',
        r'YOUR NEW BALANCE IS\s+([\d\s,\.]+)\s*XOF',
        r'NOUVEAU SOLDE\s*:\s*([\d\s,\.]+)\s*XOF',
        r'NEW BALANCE\s*:\s*([\d\s,\.]+)\s*XOF',

        #Patterns pour solde épargne Orange Bank
        r'SOLDE EPARGNE\s*:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE EPARGNE\s*:\s*([\d\s,]+)\.',
        r'SOLDE EPARGNE\s*([\d\s,]+)\s*FCFA',
        r'SOLDE D\'EPARGNE\s*:\s*([\d\s,]+)\s*FCFA',
        # Patterns pour épargne gelée Orange Bank
        r'VOUS AVEZ\s+([\d\s,]+)\s*FCFA\s+D\'EPARGNE GELEES',
        r'([\d\s,]+)\s*FCFA\s+D\'EPARGNE GELEES',
        r'EPARGNE GELEES\s+([\d\s,]+)\s*FCFA',
        r'VOUS AVEZ\s+([\d\s,]+)\s*FCFA\s+D\'EPARGNE',
        r'([\d\s,]+)\s*FCFA.*EPARGNE GELEES',
        # Patterns spécifiques ORANGE BANK
        r'SOLDE OM\s*:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE OM\s*:\s*([\d\s,]+)\.',
        r'SOLDE OM\s*([\d\s,]+)\s*FCFA',
        r'SOLDE ORANGE MONEY\s*:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE ORANGE MONEY\s*:\s*([\d\s,]+)\.',

        # Patterns pour solde avec virgules décimales (77,60)
        r'SOLDE OM\s*:\s*(\d+),(\d+)\s*FCFA',
        r'SOLDE OM\s*:\s*(\d+),(\d+)\.',

         # Pattern pour "compte principal MOOV MONEY: X FCFA"
        r'COMPTE PRINCIPAL MOOV MONEY:\s*([\d\s]+)\s*FCFA',
        r'SOLDE DE VOTRE COMPTE PRINCIPAL MOOV MONEY:\s*([\d\s]+)\s*FCFA',
        r'COMPTE PRINCIPAL:\s*([\d\s]+)\s*FCFA',
        # Pattern pour "Votre solde Moov Money est: X FCFA"
        r'VOTRE SOLDE MOOV MONEY EST:\s*([\d\s]+)\s*FCFA',
        r'SOLDE MOOV MONEY EST:\s*([\d\s]+)\s*FCFA',
        r'VOTRE SOLDE MOOV MONEY\s*:\s*([\d\s]+)\s*FCFA',

        # Patterns pour soldes avec virgules décimales
        r'VOTRE NOUVEAU SOLDE MOOV MONEY\s*([\d\s,]+)\s*FCFA',
        r'NOUVEAU SOLDE MOOV MONEY\s*([\d\s,]+)\s*FCFA',
        r'SOLDE MOOV MONEY\s*([\d\s,]+)\s*FCFA',
        r'VOTRE SOLDE MOOV MONEY\s*([\d\s,]+)\s*FCFA',
        #  Patterns FLOOZ (NOUVEAUX)
        r'VOTRE NOUVEAU SOLDE FLOOZ DU COMPTE PRINCIPAL:\s*([\d\s]+)\s*FCFA',
        r'NOUVEAU SOLDE FLOOZ DU COMPTE PRINCIPAL:\s*([\d\s]+)\s*FCFA',
        r'SOLDE FLOOZ DU COMPTE PRINCIPAL:\s*([\d\s]+)\s*FCFA',
        r'VOTRE NOUVEAU SOLDE FLOOZ:\s*([\d\s]+)\s*FCFA',
        r'NOUVEAU SOLDE FLOOZ:\s*([\d\s]+)\s*FCFA',
        r'SOLDE FLOOZ:\s*([\d\s]+)\s*FCFA',
        r'COMPTE PRINCIPAL:\s*([\d\s]+)\s*FCFA',
        r'VOTRE NOUVEAU SOLDE MOOV MONEY EST DE\s*([\d\.,]+)\s*FCFA',
        r'NOUVEAU SOLDE MOOV MONEY EST DE\s*([\d\.,]+)\s*FCFA',
        r'SOLDE MOOV MONEY EST DE\s*([\d\.,]+)\s*FCFA',

        # Pattern pour "Solde courant 1050 FCFA" (sans deux-points)
        r'SOLDE COURANT\s+(\d+)\s*FCFA',
        r'SOLDE COURANT\s+([\d\s,]+)\s*FCFA',
        r'SOLDE COURANT:\s*(\d+)\s*FCFA',
        r'SOLDE COURANT\s*:\s*(\d+)\s*FCFA',
        r'SOLDE\s+(\d+)\s*FCFA',
        r'SOLDE\s+([\d\s,]+)\s*FCFA',
        # Pattern pour "Solde courant: 10 FCFA"
        r'SOLDE COURANT:\s*(\d+)\s*FCFA',
        r'SOLDE COURANT\s*:\s*(\d+)\s*FCFA',
        r'SOLDE\s*:\s*(\d+)\s*FCFA',
        r'SOLDE\s*:\s*([\d\s,]+)\s*FCFA',

        #Patterns pour MTN MOMO français
        r'SOLDE ACTUEL:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE ACTUEL\s*:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE\s*ACTUEL\s*:\s*([\d\s,]+)\s*FCFA',
        #  Patterns pour MOBILE MONEY
        r'VOTRE NOUVEAU SOLDE EST DE:\s*([\d\s,]+)\s*FCFA',
        r'NOUVEAU SOLDE:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE:\s*([\d\s,]+)\s*FCFA',


         # Patterns spécifiques FLOOZ
        r'NOUVEAU SOLDE FLOOZ:\s*([\d\s,]+)\s*FCFA',
        r'SOLDE FLOOZ:\s*([\d\s,]+)\s*FCFA',
        r'NOUVEAU SOLDE:\s*([\d\s,]+)\s*FCFA',

        # Format: "NOUVEAU SOLDE DU COMPTE ***2501: 79608 XOF"
        r'NOUVEAU SOLDE DU COMPTE\s*[^*]*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'NOUVEAU SOLDE COMPTE\s*[^*]*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'NOUVEAU SOLDE[^:]*:\s*([+-]?[\d\s.,]+)\s*XOF',

        # Pattern pour "NOUVEAU SOLDE DU COMPTE ***2501: X XOF"
        r'NOUVEAU SOLDE DU COMPTE\s*[^*]+\s*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'NOUVEAU SOLDE DU COMPTE\s*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'NOUVEAU SOLDE COMPTE\s*[^*]+\s*:\s*([+-]?[\d\s.,]+)\s*XOF',

        # Patterns pour soldes NÉGATIFS avec fautes d'orthographe
        r'NOUVEAU SOLDE DISPONILE\s*EST\s*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'VOTRE NOUVEAU SOLDE DISPONILE\s*EST\s*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'NOUVEAU SOLDE DISPONI[BL]E\s*EST\s*:\s*([+-]?[\d\s.,]+)\s*XOF',

        # Patterns pour "DISPONIBLE" correct avec signes
        r'NOUVEAU SOLDE DISPONIBLE\s*EST\s*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'VOTRE NOUVEAU SOLDE DISPONIBLE\s*EST\s*:\s*([+-]?[\d\s.,]+)\s*XOF',
        r'SOLDE DISPONIBLE\s*:\s*([+-]?[\d\s.,]+)\s*XOF',

        # Patterns existants pour NSIA avec signes
        r'SOLDE\s*:\s*([+-]?[\d\.,]+)\s*XOF',
        r'SOLDE\s*:\s*([+-]?[\d\.,]+)\s*FCFA',
        r'SOLDE\s*:\s*([+-]?[\d\.,]+)\s*F',

        #  Pattern pour faute d'orthographe "DISPONILE"
        r'NOUVEAU SOLDE DISPONILE\s*EST\s*:\s*([\d\s.,]+)\s*XOF',
        r'VOTRE NOUVEAU SOLDE DISPONILE\s*EST\s*:\s*([\d\s.,]+)\s*XOF',
        r'NOUVEAU SOLDE DISPONI[BL]E\s*EST\s*:\s*([\d\s.,]+)\s*XOF',

        # Pattern existant pour "DISPONIBLE" (correct)
        r'NOUVEAU SOLDE DISPONIBLE\s*EST\s*:\s*([\d\s.,]+)\s*XOF',
        r'VOTRE NOUVEAU SOLDE DISPONIBLE\s*EST\s*:\s*([\d\s.,]+)\s*XOF',

        # Format "SOLDE : 3.755.532 XOF" (points séparateurs de milliers)
        r'SOLDE\s*:\s*([\d\.,]+)\s*XOF',
        r'SOLDE\s*:\s*([\d\.,]+)\s*FCFA',
        r'SOLDE\s*:\s*([\d\.,]+)\s*F',

        # Format "Votre Solde est de: 6196." (sans devise, avec point final)
        r'Votre Solde est de:\s*([\d\s.,]+)\.',
        r'VOTRE SOLDE EST DE:\s*([\d\s.,]+)\.',
        r'Votre solde est de:\s*([\d\s.,]+)\.',
        r'Solde est de:\s*([\d\s.,]+)\.',
        r'SOLDE EST DE:\s*([\d\s.,]+)\.',

        # Format "Votre Solde est de: 12422.00FCFA" (avec devise)
        r'Votre Solde est de:\s*([\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'VOTRE SOLDE EST DE:\s*([\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'Votre solde est de:\s*([\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'Solde est de:\s*([\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'SOLDE EST DE:\s*([\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',

        # Format "Solde 9152634" (sans devise)
        r'Solde\s+(\d+)',
        r'SOLDE\s+(\d+)',
        r'solde\s+(\d+)(?=\s|\.|$)',
        r'Solde\s+(\d+)\s+CBI',
        r'SOLDE\s+(\d+)\s+CBI',

        #  PATTERNS SPÉCIFIQUES BRIDGE BANK

        # Format "SOLDE COMPTE: 6,685,000"
        r'SOLDE COMPTE\s*:\s*([\d\s.,]+)',
        r'SOLDE COMPTE\s*:\s*([\d\s.,]+)(?=\s|$)',
        r'SOLDE\s*COMPTE\s*:\s*([\d\s.,]+)',

        # Format "Le solde est de XOF 2.506.880"
        r'Le solde est de XOF\s*([\d\s.,]+)',
        r'LE SOLDE EST DE XOF\s*([\d\s.,]+)',
        r'solde est de XOF\s*([\d\s.,]+)',

        #  PATTERNS GÉNÉRAUX (TOUTES BANQUES)

        # Format "Le solde est X.XXX.XXX F"
        r'Le solde est\s*([\d\s.,]+)\s*F',
        r'LE SOLDE EST\s*([\d\s.,]+)\s*F',
        r'solde est\s*([\d\s.,]+)\s*F',

        # Patterns pour soldes avec signes négatifs/positifs
        r'Solde\s*:\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'SOLDE\s*:\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'solde\s*:\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'Compte d\'epargne.*Solde\s*:\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'COMPTE D\'EPARGNE.*SOLDE\s*:\s*([+-]?\s*[\d\s,]+\.?\d*)',

        # Patterns pour "est de" avec signes
        r'est de\s*([+-]?\s*[\d\s,]+\.?\d*)\s*(?:XOF|FCFA|USD|EUR)',
        r'solde de votre compte.*est de\s*([+-]?\s*[\d\s,]+\.?\d*)\s*(?:XOF|FCFA|USD|EUR)',
        r'solde de votre compte[^*]+\s+est de\s*([+-]?\s*[\d\s,]+\.?\d*)\s*(?:XOF|FCFA|USD|EUR)',
        r'LE SOLDE DE VOTRE COMPTE[^*]+\s+EST DE\s*([+-]?\s*[\d\s,]+\.?\d*)\s*(?:XOF|FCFA|USD|EUR)',

        # Patterns pour "Dispo" avec signes
        r'Dispo\s*XOF\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'DISPO\s*XOF\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'DISPO[:\s]*XOF\s*([+-]?\s*[\d\s,]+\.?\d*)',

        # Patterns pour solde disponible avec signes
        r'Votre solde disponible est\s*XOF\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'SOLDE DISPONIBLE[:\s]*XOF\s*([+-]?\s*[\d\s,]+\.?\d*)',
        r'VOTRE SOLDE DISPONIBLE EST[:\s]*XOF\s*([+-]?\s*[\d\s,]+\.?\d*)',

        # Patterns français avec signes
        r'SOLDE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)(?=\s|\.|$)',
        r'SOLDE[:\s]*(?:EST[:\s]*)?([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)(?=\s|\.|$)',
        r'NOUVEAU SOLDE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'SOLDE COMPTE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'SOLDE DISPONIBLE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',

        # Patterns anglais avec signes
        r'BALANCE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'AVAILABLE BALANCE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'YOUR BALANCE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'CURRENT BALANCE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'ACCOUNT BALANCE[:\s]*([+-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',

        # Pattern général avec signes
        r'(?:SOLDE|BALANCE).*(?:XOF|FCFA|USD|EUR)\s*([+-]?\s*[\d\s.,]+)(?=\s|\.|$)',

        # PATTERNS DE FALLBACK (DERNIER RECOURS)

        # Patterns généraux sans devise
        r'SOLDE\s*:\s*([+-]?\s*[\d\s.,]+)(?=\s|\.|$)',
        r'SOLDE\s+([+-]?\s*[\d\s.,]+)(?=\s|\.|$)',
        r'solde\s*:\s*([+-]?\s*[\d\s.,]+)(?=\s|\.|$)',

        # Patterns pour nouveaux soldes
        r'NOUVEAU SOLDE\s*:\s*([\d\s.,]+)',
        r'NEW BALANCE\s*:\s*([\d\s.,]+)',

        # Patterns pour soldes après opération
        r'APRES OPERATION\s*:\s*([\d\s.,]+)',
        r'AFTER TRANSACTION\s*:\s*([\d\s.,]+)',

        # Pattern général avec signes
        r'(?:SOLDE|BALANCE).*(?:XOF|FCFA|USD|EUR)\s*([+-]?\s*[\d\s.,]+)(?=\s|\.|$)'
    ]


    for pattern in patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            amount_str = match.group(1).strip()


            amount_str = re.sub(r'\s+', '', amount_str)

            # Normaliser les signes
            amount_str = re.sub(r'\s*-\s*', '-', amount_str)
            amount_str = re.sub(r'\s*\+\s*', '+', amount_str)

            # CORRECTION MANUELLE pour formats problématiques (EXISTANT)
            if '.' in amount_str:
                parts = amount_str.split('.')
                if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
                    amount_str = amount_str.replace('.', '')
                elif len(parts) == 2 and len(parts[1]) == 3:
                    amount_str = amount_str.replace('.', '')

            if ',' in amount_str:
                parts = amount_str.split(',')
                if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
                    amount_str = amount_str.replace(',', '')
                elif len(parts) == 2 and len(parts[1]) == 3:
                    amount_str = amount_str.replace(',', '')

            amount = parse_currency_amount(amount_str)

            if amount is not None:

                return amount


    return None
