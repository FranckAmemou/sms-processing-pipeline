import re
from utils.helpers import parse_currency_amount, is_valid_phone_number, is_valid_counterparty_name
class CounterpartyExtractor:
    def extract(self, normalized_body, transaction_type):
        # ==========================================================================
        # DÉTECTION DES MESSAGES INFORMATIQUES (À EXCLURE)
        # ==========================================================================

        normalized_upper = normalized_body.upper()
        if "DOTATION MENSUELLE" in normalized_upper:
            return None, None
        if 'REMISE DE CHEQUE'in normalized_upper:
            return None, None

        if "RETRAIT" in normalized_upper and "EFFECTUE PAR" in normalized_upper and "FRAIS:" in normalized_body:
            return None,None
        if "FRAIS" in normalized_upper and "REMBOURSER" in normalized_upper:
            return None, None
        if "ALERTE DEBIT:" in normalized_upper and "MOBILE MONEY" in normalized_upper:
            return None, None
        if "ALERTE DEBIT:" in normalized_upper and "FRAIS" in normalized_upper:
            return None, None
        if "RETIRE DU CPTE" in normalized_upper or "VERSE SUR LE CPTE" in normalized_upper:
            return None, None
        if "DBIT DU CPTE" in normalized_upper or "CREDIT AU AC" in normalized_upper:
            return None, None
        if "CRACDIT TO AC" in normalized_upper or "DEBITED FROM AC" in normalized_upper:
            return None, None
        if "DEBIT DU AC" in normalized_upper or "VOUS VENEZ DE DEPOSER"in normalized_upper:
            return None, None
        if "BNIONLINE" in normalized_upper and "ALERTE" in normalized_upper:
            return None, None
        if ("BNIONLINE" in normalized_upper and "VIREMENT" in normalized_upper) or ("BRIDGE BANK" in normalized_upper and "RETRAITS" in normalized_upper):
            return None, None
        if ("BRIDGE BANK" in normalized_upper and "VIREMENTS RECUS" in normalized_upper) or ("BRIDGE BANK" in normalized_upper and "RETRAITS" in normalized_upper):
            return None, None
        if ("BRIDGE BANK" in normalized_upper and "PAIEMENTS" in normalized_upper) or ("VOTRE COMPTE COURANT" in normalized_upper and "UN CHEQUE" in normalized_upper):
            return None, None
        if ("VOTRE COMPTE COURANT" in normalized_upper and "UN VIREMENT" in normalized_upper) or ("BRIDGE BANK" in normalized_upper and "VIREMENTS EMIS" in normalized_upper):
            return None, None
        if ("VOTRE COMPTE COURANT" in normalized_upper and "UN PAIEMENT" in normalized_upper) or ("VOTRE COMPTE COURANT" in normalized_upper and "UN RETRAIT" in normalized_upper):
            return None, None
        if "SOLDE ACTUEL" in normalized_upper and "CHOISISSEZ" in normalized_upper:
            return None, None
        if "LE SOLDE DU COMPTE" in normalized_body and "AU" in normalized_body and 'EST DE' in normalized_body :
            return None, None
        if "LE DEBIT DE" in normalized_body and "PAR" in normalized_body and 'SODECI' in normalized_body :
            return 'SODECI', None
        if "LE DEBIT DE" in normalized_body and "PAR" in normalized_body and 'PAR PACKS MTN' in normalized_body :
            return None, None
        if "VOUS AVEZ RECU" in normalized_body and "DE DJAMO" in normalized_body and 'NOUVEAU SOLDE' in normalized_body :
            return 'DJAMO', None
        if "TRANSFERT" in normalized_body and "VERS VOTRE EPARGNE" in normalized_body and 'TIK TAK' in normalized_body :
            return "TIK TAK", None
        if "ORANGE MONEY VERS TRESORMONEY" in normalized_upper:
            return 'ORANGE MONEY',None
        if "MTN BUNDLES" in normalized_upper:
            return None, None
        if "CREDIT DE COMMUNICATION" in normalized_upper:
            return None, None
        if "MTN" in normalized_upper and "PAIEMENT" in normalized_upper and "CREDIT DE COMMUNICATION" in normalized_upper:
            return None, None
        if "VOUS AVEZ RECU" in normalized_upper and 'DE CREDIT DU' in normalized_upper:
            return None, None
        if 'VOTRE TRANSFERT' in normalized_upper and 'A ETE EFFECTUE AVEC SUCCES' in normalized_upper:
            return None, None
        if 'LE SOLDE DE VOTRE COMPTE PRINCIPAL MOOV' in normalized_upper and 'MOOV MONEY'in normalized_upper:
            return None, None
        if "ORANGE BANK" in normalized_upper and "REMBOURSE" in normalized_upper:
            return "ORANGE BANK",None
        if "TRANSFERT D'ARGENT VERS LE COMPTE BANCAIRE REUSSI"in normalized_upper:
            return None, None
        if "WAVE" in normalized_body and "CORIS BANK" in normalized_body:
            if "VERS VOTRE COMPTE WAVE" in normalized_body:
                return "CORIS BANK", None  # Coris Bank vous envoie de l'argent

        if any(phrase in normalized_upper for phrase in [
            'PAIEMENT DE', 'PAYMENT OF', 'YOUR PAYMENT OF'
        ]) and any(merchant in normalized_upper for merchant in [
            'FACEBK', 'FACEBOOK', 'AMAZON','ALIBABA','FB','JUMIA']):
            for merchant in [ 'FACEBK', 'FACEBOOK', 'AMAZON','ALIBABA']:

                return merchant,None

        #  Remboursement CISSERVICE
        if "REMBOURSEMENT" in normalized_upper and "CISSERVICE" in normalized_upper:
            return "CISSERVICE",None
        if (
            "INTERETS" in normalized_upper and
            "ORANGE BANK" in normalized_upper and
            "EPARGNE" in normalized_upper
        ):
            return "ORANGE BANK", None
        if (
            "TRANSFERT" in normalized_upper and
            "VERS" in normalized_upper and
            "ORANGE MONEY" in normalized_upper and
            "ORANGE BANK" in normalized_upper and
            "EPARGNE" in normalized_upper
        ):
            return "ORANGE BANK", None

        if (
            "TRANSFERT" in normalized_upper and
            "VERS" in normalized_upper and
            "REUSSI" in normalized_upper and
            "ORANGE BANK" in normalized_upper and
            "EPARGNE" in normalized_upper
        ):
            return "ORANGE BANK", None

        if ('LE SOLDE DE VOTRE EPARGNE' in normalized_upper and
            "ORANGE BANK" in normalized_upper ):
            return "ORANGE BANK", None
        if "EPARGNE GELES" in normalized_body and "ORANGE BANK" in normalized_body:
            return "ORANGE BANK", None
        if any(word in normalized_body.upper() for word in ['ACHAT','PAYE',"L'ACHAT"]):
            if any(action in normalized_body.upper() for action in ['GO', 'MO', 'DATA', 'INTERNET','FORFAIT INTERNET', 'FORFAIT DATA', 'ACHAT FORFAIT', 'PACK INTERNET']):
                return None,None
        # Pattern pour "par ENTREPRISE" dans les dépôts

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

                    # Nettoyer les caractères indésirables
                    counterparty_name = re.sub(r'[^A-Z0-9_&\s]', '', counterparty_name)
                    counterparty_name = counterparty_name.strip()

                    return counterparty_name, None



        if "DEPOT" in normalized_upper and "PAR" in normalized_upper:
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

                    return counterparty_name, None
        #  Format "par NUMERO - NOM/ENTREPRISE"
        if "DEPOT" in normalized_upper and "PAR" in normalized_upper:


            # Pattern principal : "par 0101459684 - CISSE VADJAHOUE/ETS CISSE"
            main_pattern = r'PAR\s+(\d+)\s*-\s*([^\.]+?)(?=\s+FRAIS|\s+TIMBRE|\s+REF|\.)'
            main_match = re.search(main_pattern, normalized_body, re.IGNORECASE)

            if main_match:
                phone_number = main_match.group(1).strip()
                counterparty_name = main_match.group(2).strip()

                # Nettoyer le nom
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name)
                counterparty_name = counterparty_name.strip()



                if is_valid_counterparty_name(counterparty_name):
                    return counterparty_name, phone_number
                else:
                    return None, phone_number

            # Fallback : format simple "par NUMERO"
            fallback_pattern = r'PAR\s+(\d+)(?=\s+FRAIS|\s+TIMBRE|\s+REF|\.|\s+VOTRE)'
            fallback_match = re.search(fallback_pattern, normalized_upper)
            if fallback_match:
                phone_number = fallback_match.group(1).strip()
                return None, phone_number

        # Envoi d'argent simple "Vous avez envoye X FCFA a [NUMERO]"
        if "VOUS AVEZ ENVOYE" in normalized_upper or "AVEZ ENVOYE" in normalized_upper:

            # Pattern 1 : "envoye X FCFA a [NOM] [NUMERO]" (nom et numéro collés)
            envoye_with_name_pattern = r"ENVOYE\s+[\d\.,]+\s*FCFA\s+[AÀ]\s+([A-Z][A-Z\s]+?)\s+(\d{8,15})"
            name_match = re.search(envoye_with_name_pattern, normalized_body, re.IGNORECASE)
            if name_match:
                counterparty_name = name_match.group(1).strip()
                phone_number = name_match.group(2).strip()

                # Nettoyer le nom
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()



                if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):
                    return counterparty_name, phone_number
                elif is_valid_counterparty_name(counterparty_name):
                    return counterparty_name, None
                elif is_valid_phone_number(phone_number):
                    return None, phone_number

    #  "envoye X FCFA a [NUMERO]" (numéro seul)
            envoye_patterns = [
                r"ENVOYE\s+[\d\.,]+\s*FCFA\s+[AÀ]\s+(\d{8,15})",
                r"ENVOYE[^AÀ]+[AÀ]\s+(\d{8,15})",
                r"[AÀ]\s+(\d{8,15})\.\s*VOTRE",  # "a 22900000073. Votre"
            ]

            for pattern in envoye_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    phone_number = match.group(1).strip()
                    if is_valid_phone_number(phone_number):
                        return None, phone_number

    # Pattern pour "Vous avez envoye... vers NUMERO - NOM"
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

                    # Nettoyer le nom
                    recipient_name = re.sub(r'\s+', ' ', recipient_name).strip()


                    return recipient_name, recipient_phone

            # Fallback : extraire seulement le numéro du destinataire
            phone_pattern = r'VERS LE\s+(\d+)(?=\s+-\s+[A-Z])'
            phone_match = re.search(phone_pattern, normalized_upper)
            if phone_match:
                recipient_phone = phone_match.group(1).strip()
                return None, recipient_phone


        # Pattern pour envoi à un agent
        if "AGENT" in normalized_upper and any(word in normalized_upper for word in ['ENVOYE', 'RETIRE', 'RETRAIT']):
            # Pattern pour extraire le numéro d'agent
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
                    return None, agent_number

            # Fallback : chercher n'importe quel long numéro après "agent"
            fallback_match = re.search(r"AGENT[^\d]*(\d{10,15})", normalized_body, re.IGNORECASE)
            if fallback_match:
                agent_number = fallback_match.group(1).strip()
                return None, agent_number

        if "AVEZ RECU UN TRANSFERT" in normalized_upper or "RECU UN TRANSFERT" in normalized_upper:
            # Pattern pour capturer le nom et le numéro
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

                    if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):
                        return counterparty_name, phone_number
                    elif is_valid_counterparty_name(counterparty_name):
                        return counterparty_name, None
                    elif is_valid_phone_number(phone_number):
                        return None, phone_number

        # extraire seulement le nom
            nom_pattern = r'DE\s+([A-Z][A-Z\s]+)(?=\s*\(|\s+LE\s+\d{4}-\d{2}-\d{2}|\s+REFERENCE|\s|$)'
            nom_match = re.search(nom_pattern, normalized_body, re.IGNORECASE)
            if nom_match:
                counterparty_name = nom_match.group(1).strip()
                if is_valid_counterparty_name(counterparty_name):
                    return counterparty_name, None


    # Pattern pour transferts GIMAC "de la part de"
        if "GIMAC" in normalized_upper and "TRANSFERT" in normalized_upper:


            gimac_patterns = [
                r'DE LA PART DE\s+(\d{8,15})',
                r'PART DE\s+(\d{8,15})',
                r'DE\s+(\d{8,15})(?=\s*\.\s*VOTRE)'
            ]

            for pattern in gimac_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    phone_number = match.group(1).strip()

                    return None, phone_number

        # chercher n'importe quel numéro après "GIMAC"
            fallback_pattern = r'GIMAC[^\d]*(\d{8,15})'
            fallback_match = re.search(fallback_pattern, normalized_body)
            if fallback_match:
                phone_number = fallback_match.group(1).strip()
                return None, phone_number
        # Pattern spécifique pour Flooz "de XXXX - NOM"
        if "FLOOZ" in normalized_upper and "RECU" in normalized_upper:


            # Pattern pour "de 800162 - HUB2"
            flooz_pattern = r'DE\s+(\d+)\s*-\s*([A-Z0-9][A-Z0-9\s]*)'
            match = re.search(flooz_pattern, normalized_body, re.IGNORECASE)
            if match:
                counterparty_code = match.group(1).strip()
                counterparty_name = match.group(2).strip()



                if is_valid_counterparty_name(counterparty_name):
                    return counterparty_name, counterparty_code
                else:
                    return None, None

        #  Pattern pour réception via agent
        if "VOUS AVEZ RECU" in normalized_upper and "AGENT" in normalized_upper:


            # Pattern pour "de l'agent ETS FATOU SERVICES COM 2290194799396"

            agent_patterns = [
                r"DE\s+L['`´']?\s*AGENT\s+([A-Z][A-Z0-9\s]+?)\s+(\d{10,15})",
                r"AGENT\s+([A-Z][A-Z0-9\s]+?)\s+(\d{10,15})"
            ]

            for pattern in agent_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    agent_name = match.group(1).strip()
                    agent_phone = match.group(2).strip()



                    # Nettoyer le nom
                    agent_name = re.sub(r'\s+', ' ', agent_name).strip()

                    if is_valid_counterparty_name(agent_name) and is_valid_phone_number(agent_phone):
                        return agent_name, agent_phone
                    elif is_valid_counterparty_name(agent_name):
                        return agent_name, None
                    elif is_valid_phone_number(agent_phone):
                        return None, agent_phone

            # Fallback : extraire nom et numéro séparément

            name_pattern = r"DE\s+L['`´']?\s*AGENT\s+([A-Z][A-Z0-9\s]+?)(?=\s+\d{10,15}|\s+[Ll][Ee]\s|\s+[Mm]otif|\s|$)"
            name_match = re.search(name_pattern, normalized_body, re.IGNORECASE)
            if name_match:
                agent_name = name_match.group(1).strip()
                agent_name = re.sub(r'\s+', ' ', agent_name).strip()

        # Chercher le numéro après le nom
                phone_after_name = re.search(rf"{re.escape(agent_name)}\s+(\d{{10,15}})", normalized_body, re.IGNORECASE)
                if phone_after_name:
                    agent_phone = phone_after_name.group(1).strip()
                    if is_valid_phone_number(agent_phone):
                        return agent_name, agent_phone
                else:
                    # Si pas de numéro, retourner juste le nom
                    if is_valid_counterparty_name(agent_name):
                        return agent_name, None
        #  Cas où "de ." est vide
        if "VOUS AVEZ RECU" in normalized_upper and "DE ." in normalized_upper:

            return None, None
        # DÉTECTION SPÉCIFIQUE POUR TRANSACTIONS UBA AVEC MARCHANDS
        if "VOUS AVEZ RECU" in normalized_upper and "UBA" in normalized_upper:
            print("[DEBUG] Transaction UBA avec marchand détectée")

            # Liste des marchands connus
            known_merchants = [
                'FACEBK', 'FACEBOOK', 'AMAZON', 'ALIBABA', 'FB', 'JUMIA',
                'GLOVO RIDERS', 'GLOVO COURIERS', 'YANGO', 'GLOVO'
            ]

            # Chercher le premier marchand trouvé dans le message
            for merchant in known_merchants:
                if merchant in normalized_upper:
                    print(f"[DEBUG] Marchand trouvé: {merchant}")
                    return merchant, None

            # Fallback: essayer d'extraire le nom après "DE"
            de_match = re.search(r'RECU[^DE]*DE\s+([A-Z][A-Z0-9\s]+?)(?=\s+POUR:|\s+NOUVEAU|\s+SOLDE|$)', normalized_upper)
            if de_match:
                merchant_name = de_match.group(1).strip()
                if len(merchant_name) > 2:  # Éviter les noms trop courts
                    print(f"[DEBUG] Marchand extrait après 'DE': {merchant_name}")
                    return merchant_name, None
        #  Pattern amélioré pour réceptions Moov Money
        if "VOUS AVEZ RECU" in normalized_upper and "MOOV MONEY" in normalized_upper:


            # Pattern pour extraire le numéro si présent
            phone_pattern = r'DE\s+(\d{8,15})'
            phone_match = re.search(phone_pattern, normalized_upper)
            if phone_match:
                phone_number = phone_match.group(1).strip()
                return None, phone_number

            # Si pas de numéro, retourner expéditeur inconnu
            return None, None

        #  Pattern pour réception simple "recu X de Y"
        elif "VOUS AVEZ RECU" in normalized_upper:


            # Pattern pour "recu X FCFA de [nom/numéro]"
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

                    if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):
                        return counterparty_name, phone_number

            # Fallback : chercher seulement le numéro
            phone_pattern = r'RECU[^DE]*DE[^\d]*(\d{8,15})'
            phone_match = re.search(phone_pattern, normalized_body, re.IGNORECASE)
            if phone_match:
                phone_number = phone_match.group(1).strip()
                if is_valid_phone_number(phone_number):
                    return None, phone_number
        # ==========================================================================
        # CORRECTION CRITIQUE : NE PAS EXTRAIRE "XOF" COMME NOM DE CONTREPARTIE
        # ==========================================================================

        # DÉTECTION SPÉCIFIQUE POUR SMS AFGMOBILE FORMAT DÉBIT
        if ("CHER(E) CLIENT(E)" in normalized_upper and
            "COMPTE ***********" in normalized_upper and
            "A ETE DEBITE DE XOF" in normalized_upper):
            print("[DEBUG COUNTERPARTY] SMS AFG Mobile débit détecté - contrepartie inconnue")
            return None, None  # Pas de contrepartie spécifique pour les débits internes

        # Détection spécifique pour Green Pay
        if ("GREEN PAY" in normalized_upper and
            "ORANGE MONEY" in normalized_upper and
            "PAIEMENT" in normalized_upper):

            return None, None
        # ==========================================================================
        # CORRECTION PRINCIPALE : PATTERN PAIEMENT POUR NOMS COMPLETS
        # ==========================================================================
        if "PAIEMENT"in normalized_upper and "DE VOTRE PRIME" in normalized_upper and "A ETE EFFECTUE"in normalized_upper:
            return None, None
        # Pattern amélioré pour capturer les noms complets avec espaces
        if "PAIEMENT DE" in normalized_upper or "TRANSFERT EFFECTUE" in normalized_upper:


            # Patterns améliorés pour capturer les noms complets (en préservant la casse)
            paiement_patterns = [
                # Pattern 1 : Capture tout jusqu'à la parenthèse avec téléphone
                r'[àa]\s+([A-Z][A-Za-z\s]+?)\s*\((\d{8,15})\)',

                # Pattern 2 : Nom Prénom (téléphone)
                r'[àa]\s+([A-Z]+(?:\s+[A-Z][a-z]+)+)\s*\((\d{8,15})\)',

                # Pattern 3 : Capture flexible
                r'[àa]\s+([^\(]+?)\s*\((\d{8,15})\)',
            ]

            for pattern in paiement_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    counterparty_name = match.group(1).strip()
                    phone_number = match.group(2).strip()



                    # Nettoyer le nom - enlever "a " ou "à " au début si présent
                    counterparty_name = re.sub(r'^\s*[àaÀA]\s+', '', counterparty_name, flags=re.IGNORECASE)
                    # Normaliser les espaces multiples
                    counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()

                    # Convertir en format titre (Première lettre en majuscule)
                    counterparty_name = ' '.join(word.capitalize() for word in counterparty_name.split())



                    # Validation
                    if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):
                        return counterparty_name, phone_number
                    elif is_valid_counterparty_name(counterparty_name):
                        return counterparty_name, None
                    elif is_valid_phone_number(phone_number):
                        return None, phone_number

            # Fallback : extraire seulement le nom complet sans téléphone
            nom_pattern = r'[àa]\s+([A-Z][A-Za-z\s]{2,}?)(?=\s*\(|\s+[lL][eE]\s+\d{4}-\d{2}-\d{2}|\s+[aA]\s+[eE][tT][eE]|\s|$)'
            nom_match = re.search(nom_pattern, normalized_body, re.IGNORECASE)
            if nom_match:
                counterparty_name = nom_match.group(1).strip()
                counterparty_name = re.sub(r'^\s*[àaÀA]\s+', '', counterparty_name, flags=re.IGNORECASE)
                counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                counterparty_name = ' '.join(word.capitalize() for word in counterparty_name.split())

                if is_valid_counterparty_name(counterparty_name):

                    return counterparty_name, None
        # ==========================================================================
        # 1. RETRAITS VIA AGENT - PRIORITÉ MAXIMALE
        # ==========================================================================
            # Pattern pour retraits "vers NUMERO - NOM/RETAILER"
        if "RETRAIT" in normalized_upper and "VERS" in normalized_upper:


            retailer_patterns = [
                r'VERS LE\s+(\d+)\s*-\s*([^\.]+?)(?=\s+FRAIS|\s+REF|\.)',
                r'VERS\s+(\d+)\s*-\s*([^\.]+?)(?=\s+FRAIS|\s+REF|\.)',
                r'VERS LE\s+(\d+)\s*-\s*([^/]+)/?([^\.]*)(?=\s+FRAIS)',
            ]

            for pattern in retailer_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    retailer_phone = match.group(1).strip()
                    retailer_name = match.group(2).strip()

                    # Nettoyer le nom
                    retailer_name = re.sub(r'\s+', ' ', retailer_name).strip()
                    retailer_name = re.sub(r'^\s*/\s*|\s*/\s*$', '', retailer_name)


                    return retailer_name, retailer_phone

            # Fallback : extraire seulement le numéro du retailer
            phone_pattern = r'VERS LE\s+(\d+)(?=\s+-\s+[A-Z])'
            phone_match = re.search(phone_pattern, normalized_upper)
            if phone_match:
                retailer_phone = phone_match.group(1).strip()
                return f"Retailer {retailer_phone}", retailer_phone

        if "AVEZ RETIRE" in normalized_upper and "VIA L'AGENT:" in normalized_upper:
            print("[DEBUG COUNTERPARTY] 🔍 Format retrait via agent détecté")

            #  Pattern amélioré pour capturer TOUT le nom de l'agent jusqu'à la parenthèse
            agent_patterns = [
                # Pattern 1 : Capture tout jusqu'à la parenthèse (avec espace avant)
                r"VIA L'AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)\s+\((\d+)",

                # Pattern 2 : Capture tout jusqu'à la parenthèse (sans espace avant)
                r"VIA L'AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)\((\d+)",

                # Pattern 3 : Version plus flexible
                r"AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)\s*\((\d+)",
            ]

            for i, pattern in enumerate(agent_patterns):
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    agent_name = match.group(1).strip()
                    agent_phone = match.group(2).strip()



                    #  Nettoyage minimal pour préserver "MEJAC GEST1"
                    agent_name = re.sub(r'\s+', ' ', agent_name).strip()



                    # Validation
                    if is_valid_counterparty_name(agent_name) and is_valid_phone_number(agent_phone):

                        return agent_name, agent_phone
                    elif is_valid_counterparty_name(agent_name):

                        return agent_name, None
                    elif is_valid_phone_number(agent_phone):

                        return None, agent_phone

            # Fallback : extraire seulement le nom de l'agent sans téléphone
            agent_nom_pattern = r"VIA L'AGENT:\s*([A-Z0-9][A-Z0-9\s]+?)(?=\s*\(|\s+-|\s+SOLDE|\s|$)"
            agent_nom_match = re.search(agent_nom_pattern, normalized_body, re.IGNORECASE)
            if agent_nom_match:
                agent_name = agent_nom_match.group(1).strip()
                agent_name = re.sub(r'\s+', ' ', agent_name).strip()

                if is_valid_counterparty_name(agent_name):

                    return agent_name, None

    # ==========================================================================
    # VERSUS BANK - CORRECTION COMPLÈTE
    # ==========================================================================

        if "VERSUS BANK" in normalized_upper:


            # Pattern SPÉCIFIQUE pour Versus Bank avec format "M. NOM, votre compte"
            versus_patterns = [
                # Pattern 1: "M. ZOUZOUO, VOTRE COMPTE NR 15016330006"
                r'^([A-Z][A-Za-z\.\s]+),\s*VOTRE\s+COMPTE\s+NR',
                # Pattern 2: "M. NSIMBA LANDU, VOTRE COMPTE NR 18012530008"
                r'^([^,]+),\s*VOTRE\s+COMPTE',
                # Pattern 3: Format général avec titre + nom
                r'^(M\.|MR\.|MME\.)\s*([^,]+),\s*VOTRE',
            ]

            for i, pattern in enumerate(versus_patterns):
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:


                    if len(match.groups()) == 2:
                        # Pattern avec titre séparé: "M." + "ZOUZOUO"
                        title = match.group(1).strip()
                        name = match.group(2).strip()
                        counterparty_name = f"{title} {name}"
                    else:
                        # Pattern avec nom complet: "M. ZOUZOUO"
                        counterparty_name = match.group(1).strip()



                    # Validation
                    if is_valid_counterparty_name(counterparty_name):

                        return counterparty_name, None
                    else:
                        print(f"[DEBUG COUNTERPARTY] ❌ Nom non validé: '{counterparty_name}'")

            # Fallback: Essayer une extraction simple avant la première virgule
            if ',' in normalized_body:
                before_comma = normalized_body.split(',')[0].strip()


                if is_valid_counterparty_name(before_comma):

                    return before_comma, None


            return "VERSUS BANK", None

        # ==========================================================================
        # 1. FORMAT ANGLAIS: "You have received X XOF FROM [NAME] (PHONE)"
        # ==========================================================================

        if "YOU HAVE RECEIVED" in normalized_upper and "FROM" in normalized_upper:


            english_patterns = [
                r'FROM\s+([A-Z][A-Z\s]+)\s*\((\d{10,15})\)',
                r'FROM\s+([A-Z][A-Z\s\.]+?)\.?\s*\((\d{10,15})\)',
                r'FROM\s+([^\(]+?)\s*\((\d{10,15})\)',
            ]

            for i, pattern in enumerate(english_patterns):
                match = re.search(pattern, normalized_upper)
                if match:
                    if len(match.groups()) == 2:
                        counterparty_name = match.group(1).strip()
                        phone_number = match.group(2).strip()

                        # Nettoyer le nom
                        counterparty_name = re.sub(r'\s*\.\s*', ' ', counterparty_name)
                        counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                        counterparty_name = re.sub(r'\s+(ON|AT|YOUR|THE|FROM)$', '', counterparty_name, flags=re.IGNORECASE)
                        counterparty_name = counterparty_name.strip()



                        if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):

                            return counterparty_name, phone_number
                        elif is_valid_counterparty_name(counterparty_name):

                            return counterparty_name, None
                        elif is_valid_phone_number(phone_number):

                            return None, phone_number

            # Si aucun pattern ne match, essayer d'extraire juste le numéro
            phone_only_match = re.search(r'\((\d{10,15})\)', normalized_upper)
            if phone_only_match:
                phone_number = phone_only_match.group(1).strip()
                if is_valid_phone_number(phone_number):

                    return None, phone_number

        # ==========================================================================
        # 1B. FORMAT ANGLAIS: "You have transferred X XOF TO [NAME] (PHONE)"
        # ==========================================================================

        if "YOU HAVE TRANSFERRED" in normalized_upper and "TO" in normalized_upper:


            transfer_patterns = [
                r'TO\s+([A-Z][A-Z\s]+)\s*\((\d{10,15})\)',
                r'TO\s+([A-Z][A-Z\s\.]+?)\.?\s*\((\d{10,15})\)',
                r'TO\s+([^\(]+?)\s*\((\d{10,15})\)',
            ]

            for i, pattern in enumerate(transfer_patterns):
                match = re.search(pattern, normalized_upper)
                if match:
                    if len(match.groups()) == 2:
                        counterparty_name = match.group(1).strip()
                        phone_number = match.group(2).strip()

                        # Nettoyer le nom
                        counterparty_name = re.sub(r'\s*\.\s*', ' ', counterparty_name)
                        counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()
                        counterparty_name = re.sub(r'\s+(ON|AT|YOUR|THE|FROM|TO)$', '', counterparty_name, flags=re.IGNORECASE)
                        counterparty_name = counterparty_name.strip()

                        if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):

                            return counterparty_name, phone_number
                        elif is_valid_counterparty_name(counterparty_name):

                            return counterparty_name, None
                        elif is_valid_phone_number(phone_number):

                            return None, phone_number

            # Si aucun pattern ne match, essayer d'extraire juste le numéro
            phone_only_match = re.search(r'\((\d{10,15})\)', normalized_upper)
            if phone_only_match:
                phone_number = phone_only_match.group(1).strip()
                if is_valid_phone_number(phone_number):
                    return None, phone_number

        if "TRANSFERT D ARGENT REUSSI" in normalized_upper and "MALI" in normalized_upper:


            # Pattern pour extraire le numéro et le pays
            international_pattern = r'AU\s+(\+\d+)\s*\(([^)]+)\)'
            match = re.search(international_pattern, normalized_body, re.IGNORECASE)

            if match:
                phone_number = match.group(1).strip()  # +22378848059
                country = match.group(2).strip()       # Mali

                return None, phone_number

            # Fallback : extraire seulement le numéro
            phone_pattern = r'AU\s+(\+\d+)'
            phone_match = re.search(phone_pattern, normalized_upper)
            if phone_match:
                phone_number = phone_match.group(1).strip()
                return None, phone_number

        if "TRANSFERT D ARGENT DE" in normalized_upper and "RECU DU" in normalized_upper:
            # Extraire le service (Taptap Send)
            service_pattern = r'DE\s+([A-Z][A-Z\s]+?)\s+RECU DU'
            service_match = re.search(service_pattern, normalized_body, re.IGNORECASE)

            # Extraire le numéro international
            phone_pattern = r'RECU DU\s*(\+\d+)'
            phone_match = re.search(phone_pattern, normalized_body, re.IGNORECASE)

            service_name = service_match.group(1).strip() if service_match else "Service International"
            phone_number = phone_match.group(1).strip() if phone_match else None

            return service_name, phone_number
        # ==========================================================================
        # 2. FORMAT REMBOURSEMENT PRÊT ANGLAIS
        # ==========================================================================

        if "YOUR REPAYMENT OF" in normalized_upper and "XTRACASH" in normalized_upper:

            return "XtraCash", None

        # ==========================================================================
        # 3. FORMAT: "Le paiement de X FCFA a [NOM] a ete effectue"
        # ==========================================================================
        if "PAIEMENT"in normalized_upper and "CREDIT DE COMMUNICATION" in normalized_upper:
            return None, None

        # Détection spécifique pour reçu de paiement avec marchand
        if "RECU DE PAIEMENT" in normalized_upper and "MARCHAND:" in normalized_upper:
            # Pattern pour "Marchand: KIABI SOCOCE"
            marchand_pattern = r'MARCHAND[:\s]*([^\n,]+?)(?=\s*CODE MARCHAND|\s*MONTANT|\s*$|,)'
            match = re.search(marchand_pattern, normalized_body, re.IGNORECASE)
            if match:
                marchand_name = match.group(1).strip()
                # Nettoyer le nom
                marchand_name = re.sub(r'\s+', ' ', marchand_name).strip()
                return marchand_name, None

            # Fallback: chercher après "Marchand:"
            fallback_pattern = r'MARCHAND[:\s]*([A-Z][A-Z\s]+)'
            fallback_match = re.search(fallback_pattern, normalized_upper)
            if fallback_match:
                marchand_name = fallback_match.group(1).strip()
                return marchand_name, None

        if "PAIEMENT" in normalized_upper and "A ETE EFFECTUE" in normalized_upper:
            # Patterns pour détecter le bénéficiaire du paiement
            payment_patterns = [
                r'FCFA\s+A\s+([A-Z0-9][A-Z0-9\s\-]+?)\s+A\s+ETE\s+EFFECTUE',
                r'FCFA\s+A\s+([a-zA-Z0-9][a-zA-Z0-9\s\-]+?)\s+A\s+ETE',
                r'PAIEMENT\s+DE\s+\d+\s+FCFA\s+A\s+([A-Z0-9][A-Z0-9\s\-]+?)\s+A\s+ETE',
            ]

            for i, pattern in enumerate(payment_patterns):
                match = re.search(pattern, normalized_upper, re.IGNORECASE)
                if match:
                    service_name = match.group(1).strip()
                    # Nettoyer le nom
                    service_name = re.sub(r'\s+', ' ', service_name).strip()
                    service_name = re.sub(r'\s+(A|LE|LA|LES|DES|DU|DE|AU|AUX)$', '', service_name, flags=re.IGNORECASE)
                    service_name = service_name.strip()

                    if is_valid_counterparty_name(service_name):

                        return service_name, None
        #  Pattern spécifique pour Moov Money "au marchand NOM NUMERO"
        if "VOUS AVEZ PAYE" in normalized_upper:

            marchand_patterns = [
                r'AU MARCHAND\s+([A-Z][A-Z\s]+?)\s+(\d{8,15})',
                r'AU MARCHAND\s+([A-Z][A-Z\s]+)\s+(\d+)',
                r'MARCHAND\s+([A-Z][A-Z\s]+?)\s+(\d{8,15})'
            ]

            for pattern in marchand_patterns:
                match = re.search(pattern, normalized_body, re.IGNORECASE)
                if match:
                    counterparty_name = match.group(1).strip()
                    phone_number = match.group(2).strip()

                    # Nettoyer le nom
                    counterparty_name = re.sub(r'\s+', ' ', counterparty_name).strip()

                    if is_valid_counterparty_name(counterparty_name) and is_valid_phone_number(phone_number):
                        return counterparty_name, phone_number
                    elif is_valid_counterparty_name(counterparty_name):
                        return counterparty_name, None
                    elif is_valid_phone_number(phone_number):
                        return None, phone_number

            # Fallback : extraire seulement le nom
            nom_pattern = r'AU MARCHAND\s+([A-Z][A-Z\s]+?)(?=\s+\d{8,15}|\s+pour\s+|\s+le\s+|$)'
            nom_match = re.search(nom_pattern, normalized_body, re.IGNORECASE)
            if nom_match:
                counterparty_name = nom_match.group(1).strip()
                if is_valid_counterparty_name(counterparty_name):
                    return counterparty_name, None
            #  Pattern amélioré pour capturer "GABON GOZEM" complet
        if "VOUS AVEZ PAYE" in normalized_upper:
            # Pattern principal
            main_pattern = r'PAYE[^A]+A\s+([^\.]+)\.'
            main_match = re.search(main_pattern, normalized_body, re.IGNORECASE)

            if main_match:
                full_text = main_match.group(1).strip()
                # Supprimer le "A " au début si présent
                full_text = re.sub(r'^\s*A\s+', '', full_text, flags=re.IGNORECASE)

                # Extraire juste le nom de l'entreprise
                enterprise_pattern = r'([A-Z][A-Z\s]+)$'
                enterprise_match = re.search(enterprise_pattern, full_text)
                if enterprise_match:
                    counterparty_name = enterprise_match.group(1).strip()
                    # Nettoyer les espaces multiples
                    counterparty_name = re.sub(r'\s+', ' ', counterparty_name)
                    # Supprimer les articles finaux
                    counterparty_name = re.sub(r'\s+(LE|DE|DU|DES|ET|AND)$', '', counterparty_name, flags=re.IGNORECASE)
                    counterparty_name = counterparty_name.strip()
                    return counterparty_name, None


        # ==========================================================================
        # 4. FORMAT: "Debit de X FCFA de votre compte Mobile Money PAR [NOM] LE"
        # ==========================================================================

        if "MOBILE MONEY" in normalized_upper and "DEBIT" in normalized_upper and "PAR" in normalized_upper:


            format2_patterns = [
                            # Pattern spécifique pour votre cas
                r'PAR\s+([A-Z][A-Z0-9\s\-]+?)(?=\s+LE\s+\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})',
                r'MOBILE MONEY PAR\s+([A-Z][A-Z0-9\s\-]+?)\s+LE',
                # Pattern pour "par FREEWAN le 28-05-2025" - extraire seulement le nom
                r'PAR\s+([A-Z][A-Z0-9\s\-]+?)\s+LE\s+\d{2}-\d{2}-\d{4}',
                r'PAR\s+([A-Z][A-Z0-9\s\-]+)\s+LE\s+\d{2}/\d{2}/\d{4}',
                r'PAR\s+([A-Z][A-Z0-9\s]+?)(?=\s+LE\s+\d{2}-\d{2}-\d{4})',
                r'PAR\s+([A-Z][A-Z0-9\s\-]+)(?=\s+LE\s+\d{2}-\d{2}-\d{4}|\s+A\s+ETE|\s|$)',
                r'PAR\s+([A-Z][A-Z0-9\s\-]+?)(?=\s+LE\s+\d{2}-\d{2}-\d{4})',
                r'PAR\s+([A-Z][A-Z0-9\s\-]{2,}?)(?=\s+(?:LE\s+\d|A\s+ETE|SUR|REF|\d{2}:\d{2}:\d{2}|$))',
            ]

            for i, pattern in enumerate(format2_patterns):
                match = re.search(pattern, normalized_upper)
                if match:
                    service_name = match.group(1).strip()


                    if is_valid_counterparty_name(service_name):
                        # Nettoyer les articles à la fin
                        service_name = re.sub(r'\s+(LE|LA|LES|DES|DU|DE|A|AU|AUX)$', '', service_name, flags=re.IGNORECASE)
                        service_name = re.sub(r'\s+', ' ', service_name).strip()

                        if is_valid_counterparty_name(service_name):

                            return service_name, None

        # ==========================================================================
        # 5. RÉCEPTION MOBILE MONEY FRANÇAIS (CRÉDITS)
        # ==========================================================================

        if "MOBILE MONEY" in normalized_upper and "VOUS AVEZ RECU" in normalized_upper:


            de_patterns = [
                r'DE\s+(\d{8,15})(?=\s+SUR|\s+DATE|\s+ID|\s|$)',
                r'RECU\s+[^DE]*DE\s+(\d{8,15})',
                r'VOUS AVEZ RECU[^DE]*DE\s+(\d{8,15})',
                r'DE\s+([A-Z][A-Z0-9\-]+)(?=\s+SUR|\s+DATE|\s+ID|\s|$)',
            ]

            for pattern in de_patterns:
                match = re.search(pattern, normalized_upper)
                if match:
                    counterparty_info = match.group(1).strip()


                    if counterparty_info.isdigit() and is_valid_phone_number(counterparty_info):

                        return None, counterparty_info
                    elif is_valid_counterparty_name(counterparty_info):

                        return counterparty_info, None
                    else:
                        print(f"[DEBUG COUNTERPARTY] ⚠️ Nom invalide exclu: '{counterparty_info}'")

        # ==========================================================================
        # 6. EXCLUSIONS TRÈS SPÉCIFIQUES UNIQUEMENT
        # ==========================================================================

        exclusion_patterns = [
            r'CREDIT.*COMMUNICATION',
            r'CASHBACK2\.SP',
            r'MTN MOMO.*CREDIT DE COMMUNICATION',
            r'TRANSFERT INTERNATIONAL RECU.*FLOOZ:',
        ]

        for pattern in exclusion_patterns:
            if re.search(pattern, normalized_upper):

                return None, None

        # ==========================================================================
        # 7. DÉTECTION PAR CONTEXTE SPÉCIFIQUE
        # ==========================================================================

        # Bridge Microfinance
        if "BRIDGE MICROFINANCE" in normalized_upper:
            return "Bridge Microfinance", None

        if "XTRACASH" in normalized_upper:
            return "XtraCash", None

        # CIE
        if "CIE" in normalized_upper and any(word in normalized_upper for word in ['PAIEMENT', 'ACHAT', 'FACTURE', 'PREPAID']):
            return "CIE", None

        # VITKASH
        if "VITKASH" in normalized_upper:
            return "VITKASH", None

        # PROVINOV
        if "PROVINOV" in normalized_upper:
            return "PROVINOV", None

        # ==========================================================================
        # 8. TRANSFERTS MTN MOMO
        # ==========================================================================

        if "VOUS AVEZ TRANSFERE" in normalized_upper:
            phone_patterns = [
                r'AU\s+(\d{8,15})',
                r'AU\s+(\d+)(?=\.|,)',
                r'TRANSFERE\s+[^0-9]*(\d{8,15})'
            ]

            for pattern in phone_patterns:
                match = re.search(pattern, normalized_body)
                if match:
                    phone_number = match.group(1).strip()
                    if is_valid_phone_number(phone_number):
                        return None, phone_number

            return "MTN MOMO", None

        # ==========================================================================
        # 8B. RETRAITS CHEZ LE MARCHAND
        # ==========================================================================

        if "VOUS AVEZ RETIRE" in normalized_upper and "CHEZ LE MARCHAND" in normalized_upper:


            # Pattern pour détecter le numéro du marchand
            merchant_pattern = r'CHEZ LE MARCHAND\s+(\d{8,15})'
            match = re.search(merchant_pattern, normalized_upper)

            if match:
                phone_number = match.group(1).strip()


                if is_valid_phone_number(phone_number):

                    return None, phone_number
                else:

                    return None, None

        # ==========================================================================
        # 9. DÉTECTION GÉNÉRALE "PAR" ET "DE"
        # ==========================================================================

        # Pattern pour "DE [NUMERO]" (priorité aux numéros)
        de_phone_pattern = r'DE\s+(\d{8,15})(?=\s+SUR|\s+DEBIT|\s+SOLDE|\s|\.|$)'
        de_phone_match = re.search(de_phone_pattern, normalized_upper)
        if de_phone_match:
            phone_number = de_phone_match.group(1).strip()
            if is_valid_phone_number(phone_number):

                return None, phone_number

        # Pattern pour "PAR [NOM]" avec validation
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

                if is_valid_counterparty_name(par_name):

                    return par_name, None

        # Pattern pour "DE [NOM]" avec validation
        de_pattern = r'DE\s+([A-Z][A-Z0-9\s\-]+)(?=\s+SUR|\s+DEBIT|\s+SOLDE|\s|\.|$)'
        de_match = re.search(de_pattern, normalized_upper)
        if de_match:
            de_name = de_match.group(1).strip()
            if is_valid_counterparty_name(de_name):

                return de_name, None

        # ==========================================================================
        # 10. FALLBACK FINAL
        # ==========================================================================
        return None, None