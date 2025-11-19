import re
from src.utils.logger import get_logger
logger = get_logger(__name__)

def extract_reference(normalized_body):
    """Extrait la référence de l'opération - VERSION COMPLÈTE ET CONTEXTUELLE"""

    # Exclure les SMS d'alerte de prêt sans référence réelle
    loan_alert_keywords = ['REMBOURSER', 'REMBOURSEZ', 'ALIMENTEZ', 'PENALITE', 'RISQUEZ', 'DEMAIN']
    if any(keyword in normalized_body for keyword in loan_alert_keywords):

        return None

    # 1. RECHERCHE DE RÉFÉRENCES EXPLICITES AVEC LABELS (HAUTE PRIORITÉ)
    explicit_ref_patterns = [
        r'POUR:\s*([A-Z0-9]+\s+[A-Z0-9]+)',  # "pour: ABNF1 00259460"
        r'POUR\s*:\s*([A-Z0-9]+\s+[A-Z0-9]+)',  # "pour : ABNF1 00259460"
        r'REFERENCE\s*:\s*([A-Z0-9]+\s+[A-Z0-9]+)',  # "reference: ABNF1 00259460"
        r'REF\s*:\s*([A-Z0-9]+\s+[A-Z0-9]+)'
        r'POUR:\s*([A-Z0-9]+)\s+([A-Z0-9]+)',
        r'POUR:\s*([A-Z0-9]+\s+[A-Z0-9]+)',
        r'POUR\s+([A-Z0-9]+\s+[A-Z0-9]+)'
        r'POUR:\s*([A-Z0-9\-]+)',  # "pour: ABNF1-259525-CORADIS"
        r'REFERENCE:\s*([A-Z0-9\-]+)',  # "reference: ABNF1-259525-CORADIS"
        r'POUR\s+([A-Z0-9\-]{10,})',
        # Pattern pour ID Orange Money
        r'ID\s*:\s*([a-f0-9]{8,})',
        r'ID\s*:\s*([A-Z0-9]{8,})',
        r'ID\s*([a-f0-9]{8,})',
        r'REF\s*:\s*([A-Z0-9]+)(?=\s|\.|$)',
        r'REF\s*:\s*([A-Z0-9]{8,15})(?=\s|$)',
        r'REFERENCE\s*:\s*([A-Z0-9]+)(?=\s|\.|$)',
        r'(TOP\d{8,})',
        r'(REF\d{8,})',
        r'(TRX\d{8,})',
        r'(TXN\d{8,})',
        r'REFERENCE:\s*([^\s,\.]+)',  # "Reference: pharmacie"
        r'REFERENCE\s*:\s*([^,\.]+)',  # avec espace optionnel
        r'REF:\s*([^\s,\.]+)',
        r'REF\s*:\s*([^,\.]+)',
        r'ID\s*:\s*(\d{8,12})',
        r'ID\s*:\s*(\d+)',
        r'REF\s*:\s*([A-Z0-9]+)',
        r'REF\s*:\s*FROMMESSAGE'
        # Pattern pour MTN MOMO "ID Tr:"
        r'ID TR:\s*([^\s\-\)]+)',
        r'ID TR\s*:\s*([^\s\-\)]+)',
        r'ID\s*TR\s*:\s*(\d+)',
        #  RÉFÉRENCES GÉNÉRIQUES
        r'EXTREF:\s*([^\s\-\)]+)',
        r'REFERENCE:\s*([^\s\-\)]+)',
        r'REF\s*:\s*([^\s\-\)]+)',
        r'REF\s+([^\s\-\)]+)',
        r'ID\s*:\s*([^\s\-\)]+)',
        r'TID:\s*([^\s\-\)]+)',
        r'TRXID:\s*([^\s\-\)]+)',
        r'TRANSACTION\s*ID:\s*([^\s\-\)]+)',

        #  RÉFÉRENCES BNI ONLINE
        r'REF\s+([A-F0-9]+)',
        r'REFERENCE\s+([A-F0-9]+)',
        r'Ref\s+([A-F0-9]+)',

        #  RÉFÉRENCES FLOOZ/MOBILE MONEY
        r'TXN ID:\s*([^\s\-\)]+)',
        r'TXNID:\s*([^\s\-\)]+)',
        r'ID TRANSACTION:\s*([^\s\.,]+)',
        r'TRANSACTION ID:\s*([^\s\.,]+)',
        r'ID\s+TRANSACTION:\s*(\d+)',

        #  RÉFÉRENCES MOBILE MONEY AVEC FORMAT UUID
        r'REF:\s*([a-f0-9\-]+)',
        r'REFERENCE:\s*([a-f0-9\-]+)',

        #  RÉFÉRENCES BANCAIRES STANDARD
        r'NUMERO\s*:\s*([^\s\.,]{4,20})',
        r'N°\s*:\s*([^\s\.,]{4,20})',
        r'NO\s*:\s*([^\s\.,]{4,20})',
    ]

    for pattern in explicit_ref_patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            ref = match.group(1).strip()
            if is_plausible_reference(ref):
                cleaned_ref = clean_reference(ref)
                return cleaned_ref

    # 2. RECHERCHE DE PATTERNS DE RÉFÉRENCE CONNUS (sans label explicite)
    known_patterns = [
        #  FORMATS UUID (Mobile Money, etc.)
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',

        # FORMATS ALPHANUMÉRIQUES COMPLEXES
        r'[A-Z]{2,}\d+[A-Z0-9]*\.[A-Z0-9]+',  # Format: XX123.ABC
        r'[A-Z]+\d+[A-Z]+\d+[A-Z]+',  # Format: ABC123DEF456GHI
        r'\b[A-Z]{3,}\d{5,}[A-Z0-9]*\b',  # Format: ABC12345...

        #  FORMATS HEXADÉCIMAUX (BNI, etc.)
        r'\b[A-F0-9]{8,16}\b',

        #  FORMATS NUMÉRIQUES LONGUES (Transaction IDs)
        r'\b\d{9,12}\b',  # IDs de transaction 9-12 chiffres
    ]

    for pattern in known_patterns:
        matches = re.findall(pattern, normalized_body, re.IGNORECASE)
        for match in matches:
            #  EXCLURE LES MONTANTS
            if not re.match(r'^\d+[A-Z]{3,4}$', match) and not match.isdigit():
                if (is_plausible_reference(match) and
                    not re.match(r'\d{16}', match) and
                    not re.match(r'\d{2}/\d{2}/\d{4}', match) and
                    not re.match(r'\d{2}:\d{2}', match) and
                    not match.upper() in ['MASTERCARD', 'VISA', 'CARTE', 'DEBIT', 'CREDIT']):
                    cleaned_ref = clean_reference(match)

                    return cleaned_ref


    # 3. RECHERCHE DANS LES CONTEXTES SPÉCIFIQUES
    ref_contexts = [
        r'REF[:\s\.]+([^,\s\.]{4,30})',
        r'REFERENCE[:\s\.]+([^,\s\.]{4,30})',
        r'ID[:\s\.]+([^,\s\.]{4,30})',
        r'NUM[EÉ]RO[:\s\.]+([^,\s\.]{4,30})',
        r'CODE[:\s\.]+([^,\s\.]{4,30})',
        r'TRANSACTION[:\s\.]+([^,\s\.]{4,30})',
    ]

    for pattern in ref_contexts:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            potential_ref = match.group(1).strip()
            if is_plausible_reference(potential_ref):
                cleaned_ref = clean_reference(potential_ref)
                return cleaned_ref

    # 4. CODE ABH (si présent)
    if "ABH" in normalized_body:
        abh_match = re.search(r'(\d{1,2}[A-Z]{3}\s+[A-Z]{3})', normalized_body)
        if abh_match:
            code = abh_match.group(1).strip()
            if is_plausible_reference(code):
                return code

    # 5. RECHERCHE DE FALLBACK - DERNIERS PATTERNS
    fallback_patterns = [
        # Pattern pour capturer après "Ref:" même avec des caractères spéciaux
        r'Ref[:\s]*([^,\s\.]{4,25})(?=\s|\.|,|$)',
        # Pattern pour IDs de transaction génériques
        r'ID[:\s]*([A-Z0-9\-]{8,20})(?=\s|\.|$)',
    ]

    for pattern in fallback_patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            potential_ref = match.group(1).strip()
            # Nettoyer les caractères indésirables en début/fin
            potential_ref = re.sub(r'^[^A-Z0-9]+|[^A-Z0-9]+$', '', potential_ref)
            if is_plausible_reference(potential_ref):
                cleaned_ref = clean_reference(potential_ref)
                return cleaned_ref

    return None


def is_plausible_reference(ref):
    """Détermine si une chaîne ressemble à une référence valide - VERSION QUI EXCLUT LES MOTS COMMUNS"""
    if not ref or len(ref) < 4:
        return False

    ref_upper = ref.upper()

    #  EXCLURE LES MONTANTS AVEC DEVISE (comme "13275FCFA")
    if re.match(r'^\d+[A-Z]{3,4}$', ref_upper):

        return False

    #  Liste étendue des termes à exclure (mots français communs)
    excluded_terms = [
        'MASTERCARD', 'VISA', 'CARTE', 'CARD', 'DEBIT', 'CREDIT',
        'ACHAT', 'TPE', 'ONLINE', 'CHEZ', 'SUR', 'COMPTE', 'SOLDE',
        'FCFA', 'XOF', 'USD', 'EUR', 'ALERTE', 'DATE', 'HEURE', 'APPLE',
        'BILL', 'GLOVO', 'ORANGE', 'MTN', 'MOOV', 'WAVE', 'FLOOZ', 'MOMO',
        'MOBILE', 'MONEY', 'BANK', 'BANQUE', 'OPERATION', 'TRANSACTION',
        'SUCCES', 'REF', 'REFERENCE', 'ID', 'NUMERO', 'CODE',
        # AJOUT DES MOTS FRANÇAIS COMMUNS DANS LES ALERTES DE PRÊT
        'REMBOURSER', 'REMBOURSEZ', 'REMBOURSEMENT', 'ALIMENTEZ', 'ALIMENTEZ',
        'PENALITE', 'RISQUEZ', 'DEMAIN', 'SINON', 'VOUS', 'VOTRE', 'DES', 'UNE',
        'PRET', 'CREDIT', 'EMPRUNT', 'ECHEANCE', 'JOURS', 'RETARD', 'OBTENIR',
        'RISQUE', 'MAINTENANT', 'AUSSI', 'BIENTOT', 'DOIT', 'ETRE', 'AVANT',
        'APRES', 'POUR', 'AVEC', 'SANS', 'TOUJOURS', 'MAINTENANT'
    ]

    if ref_upper in excluded_terms:

        return False

    # EXCLURE LES DATES ET HEURES
    if re.match(r'^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$', ref):
        return False
    if re.match(r'^\d{1,2}:\d{2}$', ref):
        return False

    #  VALIDATION DES NOMBRES PURS
    if ref.isdigit():
        if len(ref) < 8:  # Les nombres de moins de 8 chiffres ne sont pas des références
            return False
        else:
            # Les nombres de 8 chiffres ou plus pourraient être des références
            return True

    # EXCLURE LES NUMÉROS DE CARTE
    if re.match(r'^\d{16}$', ref):
        return False

    #  VALIDATION POUR UUID (acceptés comme références valides)
    if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', ref, re.IGNORECASE):
        return True

    # VALIDATION POUR RÉFÉRENCES HEXADÉCIMALES (BNI, etc.)
    if re.match(r'^[A-F0-9]{8,16}$', ref):
        return True

    #  DOIT CONTENIR DES LETTRES ET DES CHIFFRES (sauf cas particuliers)
    has_letters = re.search(r'[A-Z]', ref, re.IGNORECASE)
    has_digits = re.search(r'\d', ref)

    if has_letters and has_digits:
        return True

    #  OU BIEN ÊTRE UNE LONGUE SÉQUENCE ALPHANUMÉRIQUE
    if len(ref) >= 8 and (has_letters or has_digits):
        return True

    # ACCEPTER LES UUID MÊME SANS CHIFFRES DANS CERTAINES PARTIES
    if '-' in ref and len(ref) >= 20:
        parts = ref.split('-')
        if len(parts) == 5 and all(3 <= len(part) <= 12 for part in parts):
            return True

    return False


def clean_reference(ref):
    """Nettoie une référence en supprimant les caractères indésirables"""
    if not ref:
        return ref

    # Supprimer les ponctuations finales
    ref = re.sub(r'[.,;\s]+$', '', ref)

    # Supprimer les guillemets ou parenthèses
    ref = re.sub(r'^[\'"\(\)\[\]]+|[\'"\(\)\[\]]+$', '', ref)

    # Supprimer les espaces multiples
    ref = re.sub(r'\s+', ' ', ref).strip()

    # Pour les UUID, uniformiser la casse
    if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', ref, re.IGNORECASE):
        return ref.lower()

    return ref
