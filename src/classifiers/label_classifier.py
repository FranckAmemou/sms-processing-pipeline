import re
class LabelClassifier:
    def classify(self, normalized_body, transaction_type=None):

        """Extrait le libellé de l'opération - VERSION OPTIMISÉE"""

        if "DOTATION MENSUELLE" in normalized_body:
            return "MONTHLY ALLOWANCE RENEWAL"
            # Wave transfert = INCOMING TRANSFER
        if "WAVE" in normalized_body and "TRANSFERE" in normalized_body and "VERS VOTRE COMPTE WAVE" in normalized_body:
            return "INCOMING TRANSFER"
        # Remboursement de service
        if "REMBOURSEMENT" in normalized_body and "SUR VOTRE COMPTE" in normalized_body:
            return "REFUND"
        if "RECU DE PAIEMENT" in normalized_body and "MARCHAND:" in normalized_body:
            return "PURCHASE"
        if "PAIEMENT"in normalized_body and "DE VOTRE PRIME" in normalized_body and "A ETE EFFECTUE"in normalized_body:
            return 'INCOMING TRANSFER'
        if "TRANSFERT AUTOMATIQUE" in normalized_body and "VERS VOTRE EPARGNE" in normalized_body:
            return "SAVINGS TRANSFER"
        if "ORANGE MONEY VERS TRESORMONEY" in normalized_body:
            return 'INCOMING TRANSFER'
        if "WAVE" in normalized_body and "TRANSFERE" in normalized_body and "VERS VOTRE COMPTE WAVE" in normalized_body:
            return "INCOMING TRANSFER"
    # Détection transfert Orange Bank vers Orange Money
        if (
            "TRANSFERT" in normalized_body and
            "VERS" in normalized_body and
            "ORANGE MONEY" in normalized_body and
            "ORANGE BANK" in normalized_body and
            "EPARGNE" in normalized_body
        ):
            return "SAVINGS TRANSFER"
        # Label spécifique pour remboursement de prêt avec pénalités
        if ("PRET" in normalized_body.upper() and
            "REMBOURSE" in normalized_body.upper() and
            "PENALITE" in normalized_body.upper() and
            "EPARGNE" in normalized_body.upper() and
            "DEBITE" in normalized_body.upper()):
            print("[DEBUG LABEL] Remboursement partiel prêt avec pénalités")
            return "LOAN REPAYMENT"
    # Détection épargne gelée Orange Bank
        if "EPARGNE GELES" in normalized_body and "PRET" in normalized_body:
            return "FROZEN SAVINGS"
    # Retraits = CASH WITHDRAWAL
        if "RETRAIT" in normalized_body and "VERS" in normalized_body:
            return "CASH WITHDRAWAL"

        if "UN RETRAIT" in normalized_body:
            return "CASH WITHDRAWAL"
    # 1. RECHARGES ET CRÉDITS
        if any(phrase in normalized_body for phrase in [
            'CREDIT DE COMMUNICATION', 'ACHETE CREDIT', 'RECHARGE TELEPHONIQUE',
            'RECHARGE DE CREDIT', 'ACHAT CREDIT'
        ]):
            return "MOBILE RECHARGE"

        if "ACHETE" in normalized_body and "CREDIT" in normalized_body:
            return "MOBILE RECHARGE"

    # 2. FORFAITS INTERNET
        if any(phrase in normalized_body for phrase in [
            'FORFAIT INTERNET', 'PACK INTERNET', 'FORFAIT DATA'
        ]):
            return "INTERNET PACKAGE"

    # 3. DÉPÔTS
        if any(phrase in normalized_body for phrase in [
            'UN DEPOT', 'DEPOT EFFECTUE', 'DEPOT DE'
        ]):
            return "CASH DEPOSIT"

    # 4. PAIEMENTS EN LIGNE
        if any(phrase in normalized_body for phrase in [
        'POUR L.ARTICLE', 'SEND_CHAP', 'T_SOLUTION','AMAZON','NETFIX','JUMIA'
        ]):
            return "ONLINE PAYMENT"

    # 5. ACHATS GÉNÉRIQUES
        if "ACHETE" in normalized_body or "ACHAT" in normalized_body:
            return "PURCHASE"

    # 6. TRANSFERTS
        if "RECU" in normalized_body and "DE" in normalized_body:
            return "INCOMING TRANSFER"

        if "ENVOYE" in normalized_body or "TRANSFERE" in normalized_body:
            return "OUTGOING TRANSFER"
        if any(phrase in normalized_body.upper() for phrase in [
            'UN DEPOT', 'DEPOT EFFECTUE', 'DEPOT DE', 'SUR VOTRE NUMERO'
            ]):
            return "CASH DEPOSIT"

    # Achats de données
        if any(word in normalized_body.upper() for word in ['ACHAT','PAYE',"L'ACHAT"]):
            if any(action in normalized_body.upper() for action in ['GO', 'MO', 'DATA', 'INTERNET','FORFAIT INTERNET', 'FORFAIT DATA', 'ACHAT FORFAIT', 'PACK INTERNET']):
                return "DATA PURCHASE"
            else:
                return "PURCHASE"
    #  Paiements SEND_CHAP
        if "SEND_CHAP" in normalized_body:
            return "ONLINE PAYMENT"

    #  Paiements avec référence d'article
        if "POUR L'ARTICLE" in normalized_body or "REFERENCE" in normalized_body:
            return "ONLINE PURCHASE"
    #  Paiement chez un marchand Moov Money
        if "VOUS AVEZ PAYE" in normalized_body and "MARCHAND" in normalized_body:
            return "PURCHASE"
    # Réception d'argent via agent = CASH DEPOSIT
        if "VOUS AVEZ RECU" in normalized_body and "AGENT" in normalized_body:
            return "CASH DEPOSIT"

    # Réception simple
        if "VOUS AVEZ RECU" in normalized_body or "RECU" in normalized_body:
            return "INCOMING TRANSFER"
    # Détection envoi d'argent
        if "VOUS AVEZ ENVOYE" in normalized_body or "ENVOYE" in normalized_body:
            return "OUTGOING TRANSFER"
    #  Détection spécifique Moov Money paiement
        if "VOUS AVEZ PAYE" in normalized_body:
            return 'PURCHASE'
        if "PAIEMENT DE" in normalized_body and "A ETE EFFECTUE" in normalized_body:
            return "PURCHASE"
    # Détection des PAIEMENTS EFFECTUÉS
        if "PAIEMENT EFFECTUE" in normalized_body:
            if "DATA" in normalized_body or "INTERNET" in normalized_body:
                return "DATA PURCHASE"
            else:
                return "PURCHASE"
    #  Détection des RETRAITS VIA AGENT
        if "AVEZ RETIRE" in normalized_body and "VIA L'AGENT:" in normalized_body:
            return "CASH WITHDRAWAL"
    #  Détection des TRANSFERTS EFFECTUÉS
        if "TRANSFERT EFFECTUE" in normalized_body:
            return "OUTGOING TRANSFER"
        if "TRANSFERT" in normalized_body and 'FRAIS' in normalized_body:
            return "OUTGOING TRANSFER"
    #  Détection des DÉPÔTS REÇUS
        if "DEPOT RECU" in normalized_body:
            return "CASH DEPOSIT"
        if "PAIEMENT" in normalized_body and "MTN BUNDLES" in normalized_body:
            return "MOBILE RECHARGE"
        if "SOLDE ACTUEL" in normalized_body and "CHOISISSEZ" in normalized_body:
            return 'BALANCE INFO'
        if "PAIEMENT" in normalized_body and "MTN" in normalized_body:
            return "PURCHASE"
        if "PAIEMENT" in normalized_body and "FRAIS" in normalized_body:
            return "PURCHASE"
    #  Détection format anglais
        if "YOU HAVE RECEIVED" in normalized_body and "FROM" in normalized_body:
            return "INCOMING TRANSFER"

        if "AVEZ RECU UN TRANSFERT" in normalized_body:
            return "INCOMING TRANSFER"
        if "VOUS AVEZ RECU" in normalized_body and "MOBILE MONEY" in normalized_body:
            return "INCOMING TRANSFER"
    #  Détection recouvrement de dette
        if "DEBT COLLECTION" in normalized_body or "RECOUVREMENT" in normalized_body:
            return "LOAN COLLECTION"

    #  Détection finale de recouvrement
        if "FINAL DEBT COLLECTION" in normalized_body:
            return "FINAL LOAN COLLECTION"

    #  Détection des frais de service Mobile Money
        if "DEBIT" in normalized_body and "MOBILE MONEY" in normalized_body:
            if any(service in normalized_body for service in ['CISSERVICE', 'SERVICE', 'FRAIS']):
                return "SERVICE FEE"
            else:
                return "MOBILE MONEY TRANSFER"
        if "PAYOUT" in normalized_body and "LOAN" in normalized_body:
            return "LOAN DISBURSEMENT"
        #  Détection des transferts MTN MOMO en français
        if "CIE PREPAID" in normalized_body:
            return "UTILITY PAYMENT"
        if "VOUS AVEZ TRANSFERE" in normalized_body and "MOMO" in normalized_body:
            return "OUTGOING TRANSFER"

    #  Détection des transferts MoMo génériques
        if "VOUS AVEZ TRANSFERE" in normalized_body and "SOLDE ACTUEL" in normalized_body:
            return "OUTGOING TRANSFER"
    # Détection des transferts mobile money en anglais
        if "YOU HAVE TRANSFERRED" in normalized_body and "FROM YOUR MOBILE MONEY ACCOUNT" in normalized_body:
            return "OUTGOING TRANSFER"
        if "MOMO" in normalized_body and "VOUS AVEZ RETIRE" in normalized_body:
            return "WITHDRAWAL"
        if "MTN MOMO" in normalized_body and "PAYMENT" in normalized_body and "SUCCESSFULLY" in normalized_body:
            return "PURCHASE"
    # Détection MTN MOMO en français
        if "MTN MOMO" in normalized_body and "PAIEMENT" in normalized_body:
            return "PURCHASE"
        if "MOBILE MONEY" in normalized_body and "VOUS AVEZ RECU UN DEBIT" in normalized_body:
            return "OUTGOING TRANSFER"
        # Détection des RECEPTIONS MOBILE MONEY
        if "MOBILE MONEY" in normalized_body and "VOUS AVEZ RECU" in normalized_body:
            return "INCOMING TRANSFER"
    # Détection des PAIEMENTS MOBILE MONEY AVEC MARCHAND
        if "MOBILE MONEY" in normalized_body and "LE DEBIT DE" in normalized_body:
            if any(merchant in normalized_body for merchant in ['VITKASH', 'PAIEMENT', 'ACHAT','PAR','ETE EFFECTUE AVEC SUCCES']):
                return "PURCHASE"
        if "VOUS AVEZ ACHETE" in normalized_body:
            return "PURCHASE"
        if "SUCCES DU VIREMENT" in normalized_body and "VERS" in normalized_body:
            return "OUTGOING TRANSFER"
    #  TRANSFERTS REÇUS FLOOZ
        if "FLOOZ" in normalized_body and "RECU" in normalized_body:
            if any(bank in normalized_body for bank in ['ORABANK', 'NSIA', 'BRIDGE', 'BICICI', 'SGBCI', 'ECOBANK']):
                return "INCOMING TRANSFER"
    #  NOUVEAU : Détection des DÉPÔTS via POINTS DE VENTE FLOOZ/MOOV MONEY
        if any(service in normalized_body for service in ['FLOOZ', 'MOOV MONEY']):
            if "VOUS AVEZ RECU UN DEPOT" in normalized_body or "DEPOT RECU" in normalized_body:
                if "PDV" in normalized_body or "POINT DE VENTE" in normalized_body:
                    return "CASH DEPOSIT"
    #  Détection des TRANSFERTS VERS (OUTGOING) FLOOZ
        if "FLOOZ" in normalized_body and "TRANSFERT VERS" in normalized_body and "REUSSI" in normalized_body:
            return "OUTGOING TRANSFER"

    #  Détection des TRANSFERTS INTERNATIONAUX (HAUTE PRIORITÉ)
        if "TRANSFERT INTERNATIONAL" in normalized_body and "RECU" in normalized_body:
            return "INCOMING TRANSFER"

    #  TRANSFERTS REÇUS FLOOZ
        if "FLOOZ" in normalized_body and "TRANSFERT RECU" in normalized_body:
            return "INCOMING TRANSFER"
        if "FLOOZ" in normalized_body and "TRANSFERT RECU" in normalized_body:
            return "INCOMING TRANSFER"

        if "FLOOZ" in normalized_body and "RECU" in normalized_body and "EXPEDITEUR:" in normalized_body:
            return "INCOMING TRANSFER"

        if "FLOOZ" in normalized_body and "DEPOT" in normalized_body and "RECU" in normalized_body:
            return "INCOMING TRANSFER"

    # Détection ACHAT CASHPOWER AVEC VÉRIFICATION FLOOZ
        if "FLOOZ" in normalized_body and "ACHAT" in normalized_body and "REUSSI" in normalized_body:
            if "CASHPOWER" in normalized_body or "CASH POWER" in normalized_body:
                return "UTILITY PAYMENT"
            if "COMPTEUR:" in normalized_body and "KWH:" in normalized_body:
                return "ELECTRICITY PAYMENT"

    #DÉTECTION AUTRES SERVICES FLOOZ
        if "FLOOZ" in normalized_body and "ACHAT" in normalized_body:
            # Détection des achats de crédit téléphonique
            if any(operator in normalized_body for operator in ['ORANGE', 'MTN', 'MOOV', 'TELEVI']):
                return "MOBILE RECHARGE"

            # Détection des paiements de factures
            if any(bill in normalized_body for bill in ['FACTURE', 'BILL', 'ABONNEMENT', 'CANAL+']):
                return "UTILITY PAYMENT"


        if "RETRAIT VALIDE" in normalized_body and "FLOOZ" in normalized_body:
            return "CASH WITHDRAWAL"
    # Détection PRIORITAIRE des retraits Flooz
        if "RETRAIT" in normalized_body and "FLOOZ" in normalized_body:
            return "CASH WITHDRAWAL"

    # Détection PRIORITAIRE des paiements par carte NSIA
        if "PAIEMENT" in normalized_body and "CARTE" in normalized_body and "EFFECTUE" in normalized_body:
            return "PURCHASE"

    # Détection spécifique pour format NSIA "PAIEMENT DE X XOF PAR CARTE"
        if "PAIEMENT DE" in normalized_body and "PAR CARTE" in normalized_body:
            return "PURCHASE"

    # Le reste du code existant...
        if "INT" in normalized_body and any(word in normalized_body for word in ['DU', 'AU']):
            if transaction_type == 'CREDIT':
                return "INTEREST INCOME"
            else:
                return "INTEREST PAYMENT"
        if any(frais in normalized_body for frais in ['PACK', 'AGIOS', 'COMMISSION','COTISATION', 'ABONNEMENT', 'COTISATION CARTE','PRESENTATION PRLVMT', 'PRLVMT', 'PRELEVEMENT']):
            return "BANK FEES"

    # NOUVEAUX PATTERNS POUR LES REVENUS ET TAXES
        if "INT" in normalized_body and any(word in normalized_body for word in ['DU', 'AU']):
            if transaction_type == 'CREDIT':
                return "INTEREST INCOME"
            else:
                return "INTEREST PAYMENT"

        if "PRELEVEMENT LIBERATOI" in normalized_body:
            return "TAX PAYMENT"

        if "PRELEVEMENT" in normalized_body:
            return "BANK CHARGES"

        if "RETRAIT ESP CHQ" in normalized_body:
            return "CASH WITHDRAWAL"

        if "RETRAIT ESP" in normalized_body:
            return "CASH WITHDRAWAL"

        if "RETRAIT CHQ" in normalized_body:
            return "CHECK WITHDRAWAL"

        if "ACHAT TPE/ONLINE" in normalized_body:
            return "ONLINE PURCHASE"
        if "ACHAT TPE" in normalized_body:
            return "PURCHASE"

        if "TRANSFERT D'ARGENT VERS" in normalized_body and 'REUSSI' in normalized_body:
            return 'OUTGOING TRANSFER'
        # 1. Détection des messages de solde pur (pas de transaction)
        balance_phrases = [
            'SOLDE DE VOTRE COMPTE',
            'VOTRE SOLDE EST',
            'LE SOLDE DE VOTRE COMPTE',
            'SOLDE DU COMPTE'
        ]
        if any(phrase in normalized_body for phrase in balance_phrases):
            if not any(word in normalized_body for word in ['DEBIT', 'CREDIT', 'RETRAIT', 'DEPOT', 'VIREMENT','PAIEMENT']):
                return 'BALANCE INFO'

        # 2. Détection des salaires (HAUTE PRIORITÉ)
        if any(word in normalized_body for word in ['SALAIRE', 'SALARY']):
            return "SALARY"

        # 3. Détection des opérations d'épargne
        if 'TRANSFERT' in normalized_body and 'VERS COMPTE EPARGNE' in normalized_body:
            return 'SAVINGS TRANSFER'
        if any(word in normalized_body for word in ['EPARGNE', 'SAVINGS', 'EPARNE','PEL', 'PLAN EPARGNE LOGEMENT', 'VERS PEL']):
            if 'CREDIT' in normalized_body or 'DEBIT' in normalized_body:
                if 'MENSUEL' in normalized_body:
                    return 'MONTHLY SAVINGS'
                else:
                    return 'SAVINGS TRANSFER'
            else:
                return 'SAVINGS BALANCE'

        # 4. Détection des investissements
        investment_keywords = [
            'OBLIGATIONS', 'OBLIGATION', 'SOUSCRIPTION', 'INVESTMENT',
            'SOUSCRIPTIONS', 'TITRES', 'TITRE'
        ]
        if any(word in normalized_body for word in investment_keywords):
            return 'INVESTMENT TRANSFER'

        # 5. Détection des dépôts en espèces
        if any(phrase in normalized_body for phrase in ['VERSEMENT ESPECES', 'DEPOT ESPECES', 'VERSEMENT EFFECTUE']):
            return 'CASH DEPOSIT'

        # 7. NOUVEAU : Détection des prélèvements d'assurance

            #  CORRECTION : Détection PRIORITAIRE des primes d'assurance ACP
        if "ACP" in normalized_body and "NSIA BANQUE" in normalized_body:
            return "INSURANCE PAYMENT"

        #  CORRECTION : Détection des prélèvements d'assurance ORABANK
        if "PPO ORABANK" in normalized_body or "PRIME ACP / PPO" in normalized_body:
            return "INSURANCE PAYMENT"
        insurance_keywords = ['ASSURANCE', 'ASS VIE', 'SANLAM', 'ALLIANZ', 'PRELEVEMENT ASSURANCE', 'INSURANCE','PRIME ACP','NSIA VIE']
        if any(word in normalized_body for word in insurance_keywords):
            return 'INSURANCE PAYMENT'
        if "ALERTE DEBIT COMPTE" in normalized_body and "MONTANT" in normalized_body:
            return "INCOMING TRANSFER"
        if "ALTERTE DEBIT COMPTE" in normalized_body and "MONTANT" in normalized_body:
            return "OUTGOING TRANSFER"
        if any(word in normalized_body for word in ['RETRAIT', 'RETRAIT ESPE', 'WITHDRAWAL', 'RETIRE','RETR-TPE-N','RETR']):
            return 'CASH WITHDRAWAL'
        # 6. Détection des frais
        fee_keywords = [
            'FRAIS', 'FEE', 'CHARGES', 'PACKAGE',
            'COTISATION', 'CHARGE SUR RETRAIT', 'FEE', 'CHARGE', 'FEES',
            'CION', 'RECL','COMMISS', 'CHAR'
        ]
        if any(word in normalized_body for word in fee_keywords):
            return 'FEES'

        # 7. CORRECTION : Détection des prêts et remboursements (AMÉLIORÉE)
        loan_keywords = ['PRET', 'LOAN', 'EMPRUNT', 'ECHEANCE', 'MENSUALITE', 'REMBOURSEMENT', 'PEP']
        if any(word in normalized_body for word in loan_keywords):
            if 'INTERET' in normalized_body:
                return 'LOAN INTEREST'
            elif 'REMBOURSEMENT' in normalized_body:
                return 'LOAN REPAYMENT'
            else:
                return 'LOAN REPAYMENT'

        # 9.  CORRECTION SPÉCIFIQUE BICICI : Détection des transferts MBK comme OUTGOING TRANSFER
        if "DEBIT" in normalized_body and "MBK" in normalized_body:
            return "OUTGOING TRANSFER"

        # 8. Mobile Money
        if any(service in normalized_body for service in ['ORANGEMONEY', 'ORANGE MONEY', 'MTN MONEY', 'MOOV MONEY', 'WAVE', 'FLOOZ']):
            if 'ACCOUNT TO WALLET' in normalized_body:
                return 'OUTGOING TRANSFER'
            elif 'WALLET TO ACCOUNT' in normalized_body:
                return 'INCOMING TRANSFER'
            elif any(keyword in normalized_body for keyword in ['DEPOT', 'RECHARGE', 'CREDIT']):
                return 'MOBILE MONEY DEPOSIT'
            elif any(keyword in normalized_body for keyword in ['RETRAIT', 'WITHDRAWAL']):
                return 'MOBILE MONEY WITHDRAWAL'
            else:
                return 'MOBILE MONEY TRANSFER'

        # 9. Paiements
            #  NOUVEAU : Détection spécifique des paiements par carte
        if "PAIEMENT" in normalized_body and "CARTE" in normalized_body:
            return "PURCHASE"
        if "PAIEMENT" in normalized_body and "EFFECTUE" in normalized_body:
            return "PURCHASE"
        if "DEBIT" in normalized_body and "ACHAT" in normalized_body:
            return "PURCHASE"
        if any(keyword in normalized_body for keyword in ['PMT', 'ACHAT']):
            return 'PURCHASE'

        # 10. Retraits
        if any(word in normalized_body for word in ['RETRAIT', 'RETRAIT ESPE', 'WITHDRAWAL', 'RETIRE','RETR-TPE-N','RETR']):
            return 'WITHDRAWAL'
        if any(word in normalized_body for word in ['CHECK', 'REGLMT CHQ ', 'CHQ', 'CHEQUE']):
            return 'CHECK'
        # 11. Transferts entrants (SPÉCIFIQUES)
        if "VIREMENT RECU" in normalized_body or "VIR RECU" in normalized_body or "VIR.RECU" in normalized_body:
            return "INCOMING TRANSFER"

        if "TRANSFERT RECU" in normalized_body:
            return "INCOMING TRANSFER"

        if "DEBIT" in normalized_body and "TRANSFERT" in normalized_body:
            return "INCOMING TRANSFER"
        if "VIRT" in normalized_body and "RECU" in normalized_body:
            return "INCOMING TRANSFER"

        # 12. Transferts sortants (SPÉCIFIQUES)
        if "VIREMENT EFFECTUE" in normalized_body or "VIR EFFECTUE" in normalized_body:
            return "OUTGOING TRANSFER"

        if "TRANSFERT EFFECTUE" in normalized_body:
            return "OUTGOING TRANSFER"

        # 13. Références spécifiques
        if re.search(r'REF\s*:\s*OUT', normalized_body) or 'OUT.' in normalized_body:
            return 'OUTGOING TRANSFER'

        if re.search(r'REF\s*:\s*IN', normalized_body) or 'IN.' in normalized_body:
            return 'INCOMING TRANSFER'

        # 14. Transferts génériques
        if any(phrase in normalized_body for phrase in [
            'ACCOUNT TO WALLET TRANSFER', 'TO WALLET TRANSFER'
        ]):
            return 'OUTGOING TRANSFER'

        if any(phrase in normalized_body for phrase in [
            'WALLET TO ACCOUNT TRANSFER', 'WALLET TO ACCOUNT'
        ]):
            return 'INCOMING TRANSFER'
        if 'TAXE' in normalized_body or 'TAXE SUR' in normalized_body:
            return 'TAX'


        # 16. Fallback par mots-clés GÉNÉRAUX
        if any(word in normalized_body for word in ['DEPOT', 'DEPOSIT', 'VERSEMENT', 'DEPOSER', 'VERSE','VERS. ESP','VERS.']):
            return 'CASH DEPOSIT'

        if any(word in normalized_body for word in ['VIREMENT RECU', 'CREDIT', 'RECU DE', 'VIR.RECU','VIREMENTS RECUS']):
            return 'INCOMING TRANSFER'

        if any(word in normalized_body for word in ['VIREMENT', 'ENVOI', 'ENVOYE','VIR FAV','FAV']):
            return 'OUTGOING TRANSFER'

        if any(word in normalized_body for word in ['PAIEMENT', 'PAYMENT', 'ACHAT','DEPENSES']):
            return 'PURCHASE'
        if 'DEBIT' in normalized_body and 'OPERATION' in normalized_body :
            return 'OUTGOING TRANSFER'
        if 'CREDIT' in normalized_body and 'OPERATION' in normalized_body :
            return 'OUTGOING TRANSFER'
        # 15. Extraction après "Operation :"
        operation_match = re.search(r'OPERATION[:\s]*([^\.]+)', normalized_body)
        if operation_match:
            operation_text = operation_match.group(1).strip()
            operation_text_clean = re.sub(r'[^A-Z]', ' ', operation_text).strip()
            first_word = operation_text_clean.split()[0] if operation_text_clean.split() else ""

            label_mapping = {
                'RET': 'WITHDRAWAL', 'RETRAIT': 'WITHDRAWAL',
                'VIR': 'OUTGOING TRANSFER', 'VIREMENT': 'OUTGOING TRANSFER',
                'DEPOT': 'CASH DEPOSIT', 'DEP': 'CASH DEPOSIT',
                'FRAIS': 'FEES', 'COMMISSION': 'FEES',
                'OUT': 'OUTGOING TRANSFER', 'IN': 'INCOMING TRANSFER',
                'WITHDRAWAL': 'WITHDRAWAL', 'ATM': 'ATM WITHDRAWAL',
                'CARTE': 'CARD PAYMENT', 'PAIEMENT': 'PURCHASE'
            }

            if first_word in label_mapping:
                return label_mapping[first_word]
            elif operation_text_clean:
                return operation_text_clean
        # 17. Détection basique CREDIT/DEBIT
        if 'DEBIT' in normalized_body:
            return 'OUTGOING TRANSFER'
        if 'CREDIT' in normalized_body:
            return 'INCOMING TRANSFER'

        # 18. Fallback final
        if transaction_type:
            type_mapping = {
                'DEBIT': 'BANK OPERATION',
                'CREDIT': 'BANK OPERATION',
                'LOAN': 'LOAN REPAYMENT',
                'BALANCE': 'BALANCE INFO'
            }
            return type_mapping.get(transaction_type, 'BANK OPERATION')

        return 'BANK OPERATION'

