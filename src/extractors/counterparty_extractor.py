
"""
Extracteur d'informations sur la contrepartie (nom et numéro de téléphone)
"""

import re
from core.validators import is_valid_phone_number, is_valid_counterparty_name
from utils.logger import setup_logger

logger = setup_logger(__name__)

def extract_counterparty_info(normalized_body, transaction_type):
    """
    Extrait les informations sur la contrepartie (nom et numéro de téléphone)
    
    Args:
        normalized_body: Corps du SMS normalisé
        transaction_type: Type de transaction (CREDIT, DEBIT, LOAN, etc.)
    
    Returns:
        tuple: (counterparty_name, counterparty_phone)
    """
    
    # ==========================================================================
    # FONCTIONS DE VALIDATION INTERNES

    def _is_valid_phone_number(phone):
        """Valide si une chaîne est un numéro de téléphone valide"""
        return is_valid_phone_number(phone)

    def _is_valid_counterparty_name(name):
        """Valide si un nom de contrepartie est plausible"""
        return is_valid_counterparty_name(name)

    # ==========================================================================
    # DÉTECTION DES MESSAGES INFORMATIQUES (À EXCLURE)

    normalized_upper = normalized_body.upper()

    # Messages informatifs sans contrepartie spécifique
    if any(phrase in normalized_upper for phrase in [
        "DOTATION MENSUELLE", "REMISE DE CHEQUE", "FRAIS REMBOURSER",
        "ALERTE DEBIT: MOBILE MONEY", "ALERTE DEBIT: FRAIS", "RETIRE DU CPTE",
        "VERSE SUR LE CPTE", "DBIT DU CPTE", "CREDIT AU AC", "CRACDIT TO AC",
        "DEBIT DU AC", "VOUS VENEZ DE DEPOSER", "BNIONLINE ALERTE",
        "SOLDE ACTUEL CHOISISSEZ", "LE SOLDE DU COMPTE AU EST DE",
        "MTN BUNDLES", "CREDIT DE COMMUNICATION", "DE CREDIT DU",
        "VOTRE TRANSFERT A ETE EFFECTUE AVEC SUCCES",
        "LE SOLDE DE VOTRE COMPTE PRINCIPAL MOOV MOOV MONEY",
        "TRANSFERT D'ARGENT VERS LE COMPTE BANCAIRE REUSSI"
    ]):
        return None, None

    # Transactions spécifiques avec contrepartie connue
    if "LE DEBIT DE" in normalized_body and "PAR" in normalized_body and 'SODECI' in normalized_body:
        return 'SODECI', None
    if "DEBIT" in normalized_body and "RECU" in normalized_body and 'DE CISSERVICE' in normalized_body:
        return 'CISSERVICE', None
    if "VOUS AVEZ RECU" in normalized_body and "DE DJAMO" in normalized_body and 'NOUVEAU SOLDE' in normalized_body:
        return 'DJAMO', None
    if "TRANSFERT" in normalized_body and "VERS VOTRE EPARGNE" in normalized_body and 'TIK TAK' in normalized_body:
        return "TIK TAK", None
    if "ORANGE MONEY VERS TRESORMONEY" in normalized_upper:
        return 'ORANGE MONEY', None
    if "ORANGE BANK" in normalized_upper and "REMBOURSE" in normalized_upper:
        return "ORANGE BANK", None
    if "PAIEMENT" in normalized_upper and "PRIME" in normalized_upper:
        return None, None
    if "ORANGE MONEY" in normalized_upper and "REMBOURSER" in normalized_upper:
        return None, None
    if "REMBOURSEMENT" in normalized_upper and "CISSERVICE" in normalized_upper:
        return "CISSERVICE", None
    if "WAVE" in normalized_body and "CORIS BANK" in normalized_body and "VERS VOTRE COMPTE WAVE" in normalized_body:
        return "CORIS BANK", None
    #  Détection des retraits coffre vers carte
    if ("VOUS AVEZ RETIRE" in normalized_upper and 
        "VOTRE COFFRE" in normalized_upper and 
        ("CARTE PHYSIQUE" in normalized_upper or "CARTE VIRTUELLE" in normalized_upper)):
        return None, None
    # Alertes de prêt avec pénalités
    is_loan_penalty_alert = (
        'pret' in normalized_upper and
        'penalites' in normalized_upper and
        'retard' in normalized_upper and
        any(word in normalized_upper for word in ['attention', 'alerte', 'doit etre rembourse', 'remboursez'])
    )
    if is_loan_penalty_alert:
        return None, None

    # Paiements en ligne avec marchands connus
    if any(phrase in normalized_upper for phrase in ['PAIEMENT DE', 'PAYMENT OF', 'YOUR PAYMENT OF']):
        for merchant in ['FACEBK', 'FACEBOOK', 'AMAZON', 'ALIBABA', 'FB', 'JUMIA']:
            if merchant in normalized_upper:
                return merchant, None

    # Orange Bank transactions
    if any((
        "INTERETS" in normalized_upper and "ORANGE BANK" in normalized_upper and "EPARGNE" in normalized_upper,
        "TRANSFERT" in normalized_upper and "VERS" in normalized_upper and "ORANGE MONEY" in normalized_upper and "ORANGE BANK" in normalized_upper,
        "TRANSFERT" in normalized_upper and "VERS" in normalized_upper and "REUSSI" in normalized_upper and "ORANGE BANK" in normalized_upper,
        'LE SOLDE DE VOTRE EPARGNE' in normalized_upper and "ORANGE BANK" in normalized_upper,
        "EPARGNE GELES" in normalized_body and "ORANGE BANK" in normalized_body
    )):
        return "ORANGE BANK", None

    # Achats de données/internet
    if any(word in normalized_body.upper() for word in ['ACHAT','PAYE',"L'ACHAT"]):
        if any(action in normalized_body.upper() for action in ['GO', 'MO', 'DATA', 'INTERNET','FORFAIT INTERNET', 'FORFAIT DATA', 'ACHAT FORFAIT', 'PACK INTERNET']):
            return None, None
    if "CREDITED" in normalized_upper or "VERSEMENT" in normalized_upper:
        return None, None
    # ==========================================================================
    # EXTRACTION PAR PATTERNS

    # Pattern "CHEZ [ENTREPRISE]"
    if "CHEZ" in normalized_upper:
        chez_patterns = [
            r'CHEZ\s+([A-Z][A-Z0-9_]+)(?=\s+POUR)',
            r'CHEZ\s+([A-Z][A-Z0-9_\s]+?)(?=\s+POUR)',
            r'CHEZ\s+([^\.]+?)(?=\s+POUR L.ARTICLE)',
            r'CHEZ\s+(\S+)(?=\s+POUR)',
        ]
        for pattern in chez_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                counterparty_name = match.group(1).strip()
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                counterparty_name = re.sub(r'[^A-Z0-9_&\s]', '', counterparty_name)
                counterparty_name = counterparty_name.strip()
                
                if _is_valid_counterparty_name(counterparty_name):
                    logger.debug(f"Contrepartie trouvée via 'CHEZ': {counterparty_name}")
                    return counterparty_name, None

    # Pattern "DEPOT PAR [NOM/NUMERO]"
    if "DEPOT" in normalized_upper and "PAR" in normalized_upper:
        # Format "par NUMERO - NOM/ENTREPRISE"
        main_pattern = r'PAR\s+(\d+)\s*-\s*([^\.]+?)(?=\s+FRAIS|\s+TIMBRE|\s+REF|\.)'
        main_match = re.search(main_pattern, normalized_body, re.IGNORECASE)
        if main_match:
            phone_number = main_match.group(1).strip()
            counterparty_name = main_match.group(2).strip()
            counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
            
            if _is_valid_counterparty_name(counterparty_name) and _is_valid_phone_number(phone_number):
                logger.debug(f"Contrepartie complète trouvée: {counterparty_name} - {phone_number}")
                return counterparty_name, phone_number
            elif _is_valid_counterparty_name(counterparty_name):
                logger.debug(f"Nom de contrepartie trouvé: {counterparty_name}")
                return counterparty_name, None
            elif _is_valid_phone_number(phone_number):
                logger.debug(f"Numéro de téléphone trouvé: {phone_number}")
                return None, phone_number

        # Format simple "par NUMERO"
        fallback_pattern = r'PAR\s+(\d+)(?=\s+FRAIS|\s+TIMBRE|\s+REF|\.|\s+VOTRE)'
        fallback_match = re.search(fallback_pattern, normalized_upper)
        if fallback_match:
            phone_number = fallback_match.group(1).strip()
            if _is_valid_phone_number(phone_number):
                logger.debug(f"Numéro trouvé via 'PAR': {phone_number}")
                return None, phone_number

        # Format "par ENTREPRISE"
        depot_patterns = [
            r'PAR\s+([A-Z][A-Z0-9_]+)(?=\s+FRAIS|\s+REF|\s+\.)',
            r'PAR\s+([A-Z][A-Z0-9_\s]+)(?=\s+FRAIS)',
            r'PAR\s+([^\.]+?)(?=\s+FRAIS)',
        ]
        for pattern in depot_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                counterparty_name = match.group(1).strip()
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                
                if _is_valid_counterparty_name(counterparty_name):
                    logger.debug(f"Contrepartie trouvée via 'PAR': {counterparty_name}")
                    return counterparty_name, None

    # Pattern "VOUS AVEZ ENVOYE"
    if "VOUS AVEZ ENVOYE" in normalized_upper or "AVEZ ENVOYE" in normalized_upper:
        # Format avec nom et numéro
        envoye_with_name_pattern = r"ENVOYE\s+[\d\.,]+\s*FCFA\s+[AÀ]\s+([A-Z][A-Z\s]+?)\s+(\d{8,15})"
        name_match = re.search(envoye_with_name_pattern, normalized_body, re.IGNORECASE)
        if name_match:
            counterparty_name = name_match.group(1).strip()
            phone_number = name_match.group(2).strip()
            counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
            
            if _is_valid_counterparty_name(counterparty_name) and _is_valid_phone_number(phone_number):
                logger.debug(f"Envoi avec nom et numéro: {counterparty_name} - {phone_number}")
                return counterparty_name, phone_number
            elif _is_valid_counterparty_name(counterparty_name):
                logger.debug(f"Envoi avec nom: {counterparty_name}")
                return counterparty_name, None
            elif _is_valid_phone_number(phone_number):
                logger.debug(f"Envoi avec numéro: {phone_number}")
                return None, phone_number

        # Format avec numéro seul
        envoye_patterns = [
            r"ENVOYE\s+[\d\.,]+\s*FCFA\s+[AÀ]\s+(\d{8,15})",
            r"ENVOYE[^AÀ]+[AÀ]\s+(\d{8,15})",
            r"[AÀ]\s+(\d{8,15})\.\s*VOTRE",
        ]
        for pattern in envoye_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                phone_number = match.group(1).strip()
                if _is_valid_phone_number(phone_number):
                    logger.debug(f"Numéro trouvé via 'ENVOYE': {phone_number}")
                    return None, phone_number

    # Pattern "VOUS AVEZ ENVOYE... VERS NUMERO - NOM"
    if "VOUS AVEZ ENVOYE" in normalized_upper and "VERS" in normalized_upper:
        transfer_patterns = [
            r'VERS LE\s+(\d+)\s*-\s*([^\.]+?)(?=\s+COMMISSION|\s+REF|\.)',
            r'VERS\s+(\d+)\s*-\s*([^\.]+?)(?=\s+COMMISSION|\s+REF|\.)',
            r'VERS LE\s+(\d+)\s*-\s*([^/]+)/?([^\.]*)(?=\s+COMMISSION)',
        ]
        for pattern in transfer_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                recipient_phone = match.group(1).strip()
                recipient_name = match.group(2).strip()
                recipient_name = re.sub(r'\s+', ' ', recipient_name).strip()
                
                if _is_valid_counterparty_name(recipient_name) and _is_valid_phone_number(recipient_phone):
                    logger.debug(f"Transfert VERS avec nom et numéro: {recipient_name} - {recipient_phone}")
                    return recipient_name, recipient_phone
                elif _is_valid_counterparty_name(recipient_name):
                    logger.debug(f"Transfert VERS avec nom: {recipient_name}")
                    return recipient_name, None
                elif _is_valid_phone_number(recipient_phone):
                    logger.debug(f"Transfert VERS avec numéro: {recipient_phone}")
                    return None, recipient_phone

    # Pattern "AGENT"
    if "AGENT" in normalized_upper and any(word in normalized_upper for word in ['ENVOYE', 'RETIRE', 'RETRAIT']):
        agent_patterns = [
            r"A L'AGENT\s+(\d{10,15})",
            r"AGENT\s+(\d{10,15})",
            r"A L AGENT\s+(\d{10,15})",
            r"A L\.AGENT\s+(\d{10,15})"
        ]
        for pattern in agent_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                agent_number = match.group(1).strip()
                if _is_valid_phone_number(agent_number):
                    logger.debug(f"Numéro d'agent trouvé: {agent_number}")
                    return None, agent_number

    # Pattern "AVEZ RECU UN TRANSFERT"
    if "AVEZ RECU UN TRANSFERT" in normalized_upper or "RECU UN TRANSFERT" in normalized_upper:
        transfert_patterns = [
            r'DE\s+([A-Z][A-Z\s]+)\((\d+)\)',
            r'DE\s+([A-Z][A-Z\s]+?)\s*\((\d+)\)',
            r'DE\s+([^\(]+)\s*\((\d+)\)',
        ]
        for pattern in transfert_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                counterparty_name = match.group(1).strip()
                phone_number = match.group(2).strip()
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                
                if _is_valid_counterparty_name(counterparty_name) and _is_valid_phone_number(phone_number):
                    logger.debug(f"Transfert reçu avec nom et numéro: {counterparty_name} - {phone_number}")
                    return counterparty_name, phone_number
                elif _is_valid_counterparty_name(counterparty_name):
                    logger.debug(f"Transfert reçu avec nom: {counterparty_name}")
                    return counterparty_name, None
                elif _is_valid_phone_number(phone_number):
                    logger.debug(f"Transfert reçu avec numéro: {phone_number}")
                    return None, phone_number

    # Pattern "VOUS AVEZ RECU" (réceptions)
    if "VOUS AVEZ RECU" in normalized_upper:
        # Pattern pour réception avec agent
        if "AGENT" in normalized_upper:
            agent_patterns = [
                r"DE\s+L['`´']?\s*AGENT\s+([A-Z][A-Z0-9\s]+?)\s+(\d{10,15})",
                r"AGENT\s+([A-Z][A-Z0-9\s]+?)\s+(\d{10,15})"
            ]
            for pattern in agent_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    agent_name = match.group(1).strip()
                    agent_phone = match.group(2).strip()
                    agent_name = re.sub(r'\s+', ' ', agent_name).strip()
                    
                    if _is_valid_counterparty_name(agent_name) and _is_valid_phone_number(agent_phone):
                        logger.debug(f"Réception agent avec nom et numéro: {agent_name} - {agent_phone}")
                        return agent_name, agent_phone
                    elif _is_valid_counterparty_name(agent_name):
                        logger.debug(f"Réception agent avec nom: {agent_name}")
                        return agent_name, None
                    elif _is_valid_phone_number(agent_phone):
                        logger.debug(f"Réception agent avec numéro: {agent_phone}")
                        return None, agent_phone

        # Pattern général pour réception
        recu_patterns = [
            r'RECU[^DE]*DE\s+([A-Z][A-Z0-9\s]+?)\s+(\d{8,15})',
            r'RECU[^DE]*DE\s+([^\.]+?)\s+(\d{8,15})',
            r'DE\s+([A-Z][A-Z0-9\s]+?)\s+(\d{8,15})'
        ]
        for pattern in recu_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                counterparty_name = match.group(1).strip()
                phone_number = match.group(2).strip()
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                
                if _is_valid_counterparty_name(counterparty_name) and _is_valid_phone_number(phone_number):
                    logger.debug(f"Réception avec nom et numéro: {counterparty_name} - {phone_number}")
                    return counterparty_name, phone_number

        # Pattern numéro seul
        phone_pattern = r'RECU[^DE]*DE[^\d]*(\d{8,15})'
        phone_match = re.search(phone_pattern, normalized_body, re.IGNORECASE)
        if phone_match:
            phone_number = phone_match.group(1).strip()
            if _is_valid_phone_number(phone_number):
                logger.debug(f"Numéro trouvé via 'RECU': {phone_number}")
                return None, phone_number

    # Pattern "PAIEMENT DE" avec nom complet
    if "PAIEMENT DE" in normalized_upper or "TRANSFERT EFFECTUE" in normalized_upper:
        paiement_patterns = [
            r'[àa]\s+([A-Z][A-Za-z\s]+?)\s*\((\d{8,15})\)',
            r'[àa]\s+([A-Z]+(?:\s+[A-Z][a-z]+)+)\s*\((\d{8,15})\)',
            r'[àa]\s+([^\(]+?)\s*\((\d{8,15})\)',
        ]
        for pattern in paiement_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                counterparty_name = match.group(1).strip()
                phone_number = match.group(2).strip()
                counterparty_name = re.sub(r'^\s*[àaÀA]\s+', '', counterparty_name, flags=re.IGNORECASE)
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                counterparty_name = ' '.join(word.capitalize() for word in counterparty_name.split())
                
                if _is_valid_counterparty_name(counterparty_name) and _is_valid_phone_number(phone_number):
                    logger.debug(f"Paiement avec nom et numéro: {counterparty_name} - {phone_number}")
                    return counterparty_name, phone_number
                elif _is_valid_counterparty_name(counterparty_name):
                    logger.debug(f"Paiement avec nom: {counterparty_name}")
                    return counterparty_name, None
                elif _is_valid_phone_number(phone_number):
                    logger.debug(f"Paiement avec numéro: {phone_number}")
                    return None, phone_number

    # Pattern "RETRAIT VIA AGENT"
    if "AVEZ RETIRE" in normalized_upper and "VIA L'AGENT:" in normalized_upper:
        agent_patterns = [
            r"VIA L'AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)\s+\((\d+)",
            r"VIA L'AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)\((\d+)",
            r"AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)\s*\((\d+)",
        ]
        for pattern in agent_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                agent_name = match.group(1).strip()
                agent_phone = match.group(2).strip()
                agent_name = re.sub(r'\s+', ' ', agent_name).strip()
                
                if _is_valid_counterparty_name(agent_name) and _is_valid_phone_number(agent_phone):
                    logger.debug(f"Retrait agent avec nom et numéro: {agent_name} - {agent_phone}")
                    return agent_name, agent_phone
                elif _is_valid_counterparty_name(agent_name):
                    logger.debug(f"Retrait agent avec nom: {agent_name}")
                    return agent_name, None
                elif _is_valid_phone_number(agent_phone):
                    logger.debug(f"Retrait agent avec numéro: {agent_phone}")
                    return None, agent_phone

    # Pattern VERSUS BANK
    if "VERSUS BANK" in normalized_upper:
        versus_patterns = [
            r'^([A-Z][A-Za-z\.\s]+),\s*VOTRE\s+COMPTE\s+NR',
            r'^([^,]+),\s*VOTRE\s+COMPTE',
            r'^(M\.|MR\.|MME\.)\s*([^,]+),\s*VOTRE',
        ]
        for pattern in versus_patterns:
            match = re.search(pattern, normalized_body, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    title = match.group(1).strip()
                    name = match.group(2).strip()
                    counterparty_name = f"{title} {name}"
                else:
                    counterparty_name = match.group(1).strip()
                
                if _is_valid_counterparty_name(counterparty_name):
                    logger.debug(f"Contrepartie VERSUS BANK: {counterparty_name}")
                    return counterparty_name, None
        
        return "VERSUS BANK", None

    # Patterns anglais
    if "YOU HAVE RECEIVED" in normalized_upper and "FROM" in normalized_upper:
        english_patterns = [
            r'FROM\s+([A-Z][A-Z\s]+)\s*\((\d{10,15})\)',
            r'FROM\s+([A-Z][A-Z\s\.]+?)\.?\s*\((\d{10,15})\)',
            r'FROM\s+([^\(]+?)\s*\((\d{10,15})\)',
        ]
        for pattern in english_patterns:
            match = re.search(pattern, normalized_upper)
            if match:
                if len(match.groups()) == 2:
                    counterparty_name = match.group(1).strip()
                    phone_number = match.group(2).strip()
                    counterparty_name = re.sub(r'\s*\.\s*', ' ', counterparty_name)
                    counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                    counterparty_name = re.sub(r'\s+(ON|AT|YOUR|THE|FROM)$', '', counterparty_name, flags=re.IGNORECASE)
                    counterparty_name = counterparty_name.strip()
                    
                    if _is_valid_counterparty_name(counterparty_name) and _is_valid_phone_number(phone_number):
                        logger.debug(f"Réception anglais avec nom et numéro: {counterparty_name} - {phone_number}")
                        return counterparty_name, phone_number
                    elif _is_valid_counterparty_name(counterparty_name):
                        logger.debug(f"Réception anglais avec nom: {counterparty_name}")
                        return counterparty_name, None
                    elif _is_valid_phone_number(phone_number):
                        logger.debug(f"Réception anglais avec numéro: {phone_number}")
                        return None, phone_number

    # ==========================================================================
    # FALLBACK ET DÉTECTIONS GÉNÉRALES

    # Détection par contexte spécifique
    context_mappings = {
        'BRIDGE MICROFINANCE': "Bridge Microfinance",
        'XTRACASH': "XtraCash",
        'VITKASH': "VITKASH",
        'PROVINOV': "PROVINOV"
    }
    for keyword, name in context_mappings.items():
        if keyword in normalized_upper:
            logger.debug(f"Contrepartie détectée par contexte: {name}")
            return name, None

    # CIE (Compagnie Ivoirienne d'Electricité)
    if "CIE" in normalized_upper and any(word in normalized_upper for word in ['PAIEMENT', 'ACHAT', 'FACTURE', 'PREPAID']):
        logger.debug("Contrepartie détectée: CIE")
        return "CIE", None

    # Patterns généraux "DE [NUMERO]" et "PAR [NOM]"
    de_phone_pattern = r'DE\s+(\d{8,15})(?=\s+SUR|\s+DEBIT|\s+SOLDE|\s|\.|$)'
    de_phone_match = re.search(de_phone_pattern, normalized_upper)
    if de_phone_match:
        phone_number = de_phone_match.group(1).strip()
        if _is_valid_phone_number(phone_number):
            logger.debug(f"Numéro trouvé via 'DE': {phone_number}")
            return None, phone_number

    par_patterns = [
        r'PAR\s+([A-Z][A-Z0-9\s\-]+?)(?=\s+LE\s+\d{2}-\d{2}-\d{4}|\s+A\s+ETE|\s|$)',
        r'PAR\s+([A-Z][A-Z0-9\s\-]+)(?=\s+(?:LE\s+|A\s+ETE|REF|$))',
    ]
    for par_pattern in par_patterns:
        par_match = re.search(par_pattern, normalized_upper)
        if par_match:
            par_name = par_match.group(1).strip()
            par_name = re.sub(r'\s+(LE|LA|LES|DES|DU|DE)$', '', par_name, flags=re.IGNORECASE)
            par_name = par_name.strip()
            
            if _is_valid_counterparty_name(par_name):
                logger.debug(f"Nom trouvé via 'PAR': {par_name}")
                return par_name, None

    # Pattern "DE [NOM]"
    de_pattern = r'DE\s+([A-Z][A-Z0-9\s\-]+)(?=\s+SUR|\s+DEBIT|\s+SOLDE|\s|\.|$)'
    de_match = re.search(de_pattern, normalized_upper)
    if de_match:
        de_name = de_match.group(1).strip()
        if _is_valid_counterparty_name(de_name):
            logger.debug(f"Nom trouvé via 'DE': {de_name}")
            return de_name, None

    logger.debug("Aucune contrepartie trouvée")
    return None, None
