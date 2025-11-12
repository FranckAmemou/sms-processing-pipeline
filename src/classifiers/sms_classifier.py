import re
import logging

logger = logging.getLogger(__name__)

class SMSClassifier:
    def classify(self, normalized_body):  # ✅ AJOUT DE 'self'
        """Détermine le type de SMS - VERSION COMPLÈTE ET CORRIGÉE POUR C/D"""

        if not normalized_body:
            return 'UNKNOWN'

        # Convertir en majuscules pour les comparaisons
        normalized_upper = normalized_body.upper()
        
        # DÉTECTION PRIORITAIRE PAR C/D (CRÉDIT/DÉBIT) - ABSOLUE
        if re.search(r'\bC\s+\d', normalized_upper):
            return 'CREDIT'

        if re.search(r'\bD\s+\d', normalized_upper):
            return 'DEBIT'

        #  CREDIT (argent reçu sur Wave)
        if "WAVE" in normalized_body and "TRANSFERE" in normalized_body and "VERS VOTRE COMPTE WAVE" in normalized_body:
            return 'CREDIT'
        if "VOTRE DOTATION MENSUELLE" in normalized_body :
            return 'CREDIT'  # Si vous considérez la dotation comme un crédit de service
        if "TRANSFERT D ARGENT DE" in normalized_upper and "RECU DU" in normalized_upper:
            return "CREDIT"
            
        # Remboursement = CREDIT (argent reçu)
        if any(phrase in normalized_upper for phrase in [
            'LE REMBOURSEMENT DE',
        ]) and any(keyword in normalized_upper for keyword in [
        'SUR VOTRE COMPTE'
        ]):
            return 'CREDIT'
            
        # Détection spécifique pour transfert reçu
        if ("VOUS A TRANSFERE" in normalized_upper or
            "VOUS A ENVOYE" in normalized_upper or
            "TRANSFERT RECU" in normalized_upper):
            return 'CREDIT'  # C'est un CREDIT !
            
        if "FRAIS" in normalized_upper and "REMBOURSER" in normalized_upper:
            return 'CREDIT'
        if "FRAIS" in normalized_upper and "REMBOURSE" in normalized_upper:
            return 'CREDIT'
        if "ORANGE MONEY VERS TRESORMONEY" in normalized_upper:
            return 'CREDIT'
        if "TRANSFERT AUTOMATIQUE" in normalized_upper and "VERS" in normalized_upper and "EPARGNE" in normalized_upper:
            return "CREDIT"
            
        #  Détection des transferts Orange Bank vers Orange Money
        if "TRANSFERT" in normalized_upper and "VERS"in normalized_upper and "ORANGE MONEY" in normalized_upper and 'OREANGE BANK'in normalized_upper and 'EPARGNE'in normalized_upper:
            return "DEBIT"
        if "TRANSFERT D ARGENT REUSSI" in normalized_upper:
            return "DEBIT"
        if "ORANGE BANK" in normalized_upper and "EPARGNE GELES" in normalized_upper:
            return "FROZEN"
            
        # Détection des paiements USD
        if any(phrase in normalized_upper for phrase in [
            'PAIEMENT DE', 'PAYMENT OF', 'YOUR PAYMENT OF'
        ]) and any(merchant in normalized_upper for merchant in [
            'FACEBK', 'FACEBOOK', 'AMAZON','ALIBABA'
        ]):
            return 'DEBIT'
            
        #Détection spécifique pour remboursement de prêt avec pénalités
        if ("ORANGE BANK" in normalized_upper and
            "PRET" in normalized_upper and
            "REMBOURSE" in normalized_upper and
            "EPARGNE" in normalized_upper and
            "DEBITE" in normalized_upper):
            return 'DEBIT'  # C'est un DÉBIT de l'épargne !
            
        if 'TRANSFERT' in normalized_upper and 'VERS COMPTE EPARGNE':
            return 'DEBIT'
        if any(phrase in normalized_upper for phrase in [
            'UN DEPOT', 'DEPOT EFFECTUE', 'DEPOT DE', 'A ETE EFFECTUE SUR VOTRE'
        ]):
            return 'CREDIT'
        if "VOUS AVEZ PAYE" in normalized_body:
            return 'DEBIT'
            
        # 1. TRANSACTIONS DE DÉBIT
        #  Réception = CREDIT (priorité haute)
        if "VOUS AVEZ RECU" in normalized_upper or "RECU" in normalized_upper:
                return 'CREDIT'
                
        # Patterns existants pour débits...
        if "VOUS AVEZ ENVOYE" in normalized_upper:
                return 'DEBIT'
                
        #  Détection transfert Moov Money générique
        if "TRANSFERT" in normalized_upper and "EFFECTUE" in normalized_upper:
            return 'DEBIT'
            
        # Détection "paiement de X a Y a ete effectue"
        if "PAIEMENT DE" in normalized_upper and "A ETE EFFECTUE" in normalized_upper:
            return 'DEBIT'
        if "AVEZ RETIRE" in normalized_upper:
            return 'DEBIT'
        if "DEPOT RECU" in normalized_upper or "DEPOT RECU" in normalized_upper:
            return 'CREDIT'
            
        #  Détection des PAIEMENTS EFFECTUÉS
        if "PAIEMENT EFFECTUE" in normalized_upper:
            return 'DEBIT'
        if "PAIEMENT" in normalized_upper and "MTN" in normalized_upper:
            return 'DEBIT'
            
        #  Détection format anglais "You have received"
        if "YOU HAVE RECEIVED" in normalized_upper and "FROM" in normalized_upper:
            return 'CREDIT'

        # Détection existante pour format français
        if "VOUS AVEZ RECU" in normalized_upper:
            return 'CREDIT'
            
        #Détection recouvrement de dette = DÉBIT
        if "DEBT COLLECTION" in normalized_upper and "SUCCESSFULLY COMPLETED" in normalized_upper:
            return 'DEBIT'  # Recouvrement = argent sortant

        # Détection finale de recouvrement
        if "FINAL DEBT COLLECTION" in normalized_upper:
            return 'DEBIT'

        # Détection des DÉBITS Mobile Money
        if "VOUS AVEZ RECU UN DEBIT" in normalized_upper and "MOBILE MONEY" in normalized_upper:
            return 'DEBIT'  # C'est un débit même si ça dit "vous avez reçu un débit"

        #  Détection explicite "DEBIT"
        if "DEBIT" in normalized_upper and "NOUVEAU SOLDE" in normalized_upper:
            # Vérifier le contexte pour éviter les confusions
            if not any(word in normalized_upper for word in ['CREDIT', 'RECU CREDIT', 'VIREMENT RECU']):
                return 'DEBIT'

        # Détection des DÉCAISSEMENTS DE PRÊT (PAYOUT = CREDIT)
        if "PAYOUT" in normalized_upper and "LOAN" in normalized_upper:
            return 'CREDIT'  # Payout = décaissement = argent reçu

        #Détection des remboursements de prêt
        if "LOAN REPAYMENT" in normalized_upper or "REMBOURSEMENT PRET" in normalized_upper:
            return 'DEBIT'
            
        # Détection des transferts MTN MOMO en français
        if "VOUS AVEZ TRANSFERE" in normalized_upper and "MOMO" in normalized_upper:
            return 'DEBIT'

        # Détection des transferts MoMo génériques
        if "VOUS AVEZ TRANSFERE" in normalized_upper and "SOLDE ACTUEL" in normalized_upper:
            return 'DEBIT'

        # Détection des transferts mobile money en anglais
        if "YOU HAVE TRANSFERRED" in normalized_upper and "FROM YOUR MOBILE MONEY ACCOUNT" in normalized_upper:
            return 'DEBIT'

        if "MTN MOMO" in normalized_upper and "PAYMENT" in normalized_upper and "SUCCESSFULLY" in normalized_upper:
            return 'DEBIT'

        # Détection MTN MOMO en français
        if "MTN MOMO" in normalized_upper and "PAIEMENT" in normalized_upper:
            return 'DEBIT'

        # Détection MOBILE MONEY - RECEPTION
        if "MOBILE MONEY" in normalized_upper:
            if "VOUS AVEZ RECU" in normalized_upper or "RECU" in normalized_upper:
                return 'CREDIT'
            elif "DEBIT" in normalized_upper:
                return 'DEBIT'
                
        if "MTN MOMO" in normalized_upper and "PAIEMENT" in normalized_upper:
            return 'DEBIT'
        if "MOBILE MONEY" in normalized_body and "VOUS AVEZ RECU UN DEBIT" in normalized_body:
            return "DEBIT"

        # Détection des VIREMENTS BNI ONLINE
        if "SUCCES DU VIREMENT" in normalized_upper and "VERS" in normalized_upper:
            return 'DEBIT'  # Virement émis = débit
            
        # Détection des TRANSFERTS INTERNATIONAUX REÇUS (HAUTE PRIORITÉ)
        if "TRANSFERT INTERNATIONAL" in normalized_upper and "RECU" in normalized_upper:
            return 'CREDIT'

        if "FLOOZ" in normalized_upper and "TRANSFERT VERS" in normalized_upper and "REUSSI" in normalized_upper:
            return 'DEBIT'

        # TRANSFERTS REÇUS FLOOZ = CREDIT
        if "FLOOZ" in normalized_upper:
            if "TRANSFERT RECU" in normalized_upper or "TRANSFERT INTERNATIONAL RECU" in normalized_upper:
                return 'CREDIT'
            if "RECU" in normalized_upper and "MONTANT:" in normalized_upper:
                return 'CREDIT'
            if "DEPOT" in normalized_upper and "RECU" in normalized_upper:
                return 'CREDIT'

        # DÉTECTION DES FRAIS BANCAIRES (priorité haute)
        fee_keywords = ['AGIOS', 'PACK', 'FORFAIT', 'COTISATION', 'FRAIS COMPTE', 'COMMISSION', 'FRAIS']
        if any(word in normalized_upper for word in fee_keywords):
            return 'DEBIT'

        # DÉTECTION DES PRÊTS (priorité haute)
        loan_keywords = ['PRETIELLEMENT REMBOURSE', 'partiellement rembourse', 'EMPRUNT', 'ECHEANCE', 'MENSUALITE', 'REMBOURSEMENT']
        if any(word in normalized_upper for word in loan_keywords):
            return 'DEBIT'

        #  CORRECTION : SGCNCT - déterminer selon le contexte
        if "SGCNCT" in normalized_upper:
            # SGCNCT avec VIR FAV = virement entre comptes = généralement CRÉDIT
            if "VIR FAV" in normalized_upper or "VIR FAV CPT" in normalized_upper:
                return 'CREDIT'
            # SGCNCT avec VIR AUTRE = virement vers autre banque = DÉBIT
            elif "VIR AUTRE" in normalized_upper:
                return 'DEBIT'
            # Par défaut, considérer SGCNCT comme transaction
            else:
                return 'DEBIT'

        #  DÉTECTION DES TRANSACTIONS DÉBIT
        debit_keywords = [
            'DEBITE', 'DEBIT', 'RETRAIT', 'MONTANT DEBITE', 'PAIEMENT',
            'EFFECTUE', 'RETIRE', 'DEBITED', 'WITHDRAWAL', 'TRANSFERT D\'ARGENT VERS',
            'PRELEVEMENT', 'PRLVMT', 'PRESENTATION PRLVMT', 'ACHAT', 'FACTURATION',
            'RETRAIT DAB', 'RETRAIT GUICHET'
        ]

        # Détection prioritaire des transferts CORIS
        if "TRANSFERT D'ARGENT VERS" in normalized_upper and 'REUSSI' in normalized_upper:
            return 'DEBIT'

        # Détection des paiements effectués
        if "PAIEMENT" in normalized_upper and "EFFECTUE" in normalized_upper:
            return 'DEBIT'

        # Détection des transactions avec "Transaction" + "effectue"
        if "TRANSACTION" in normalized_upper and "EFFECTUE" in normalized_upper:
            return 'DEBIT'

        # Détection générale des débits
        if any(word in normalized_upper for word in debit_keywords):
            return 'DEBIT'

        # DÉTECTION DES DÉPÔTS ET CRÉDITS
        credit_keywords = [
            'CREDIT', 'CREDITE', 'DEPOT', 'VIREMENT RECU', 'VERSEMENT',
            'RECU', 'CREDITED', 'DEPOSIT', 'DEPOSER', 'VIREMENTS RECUS',
            'SALAIRE', 'SALARY', 'REVENU', 'INTERET', 'INTEREST'
        ]

        if any(word in normalized_upper for word in credit_keywords):
            return 'CREDIT'

        #  DÉTECTION DES PAIEMENTS EN LIGNE
        if any(merchant in normalized_upper for merchant in ['APPLE.COM/BILL', 'ITUNES.COM', 'GOOGLE', 'PLAY STORE', 'AMAZON', 'NETFLIX']):
            return 'DEBIT'

        #  DÉTECTION DES TRANSACTIONS GÉNÉRIQUES
        if 'TRANSACTION' in normalized_upper and not 'BALANCE' in normalized_upper:
            return 'DEBIT'

        #  DÉTECTION DES ASSURANCES ET TAXES
        insurance_tax_keywords = ['ASSURANCE', 'TAXE', 'PRELEVEMENT', 'COTISATION ASSURANCE', 'TAX']
        if any(word in normalized_upper for word in insurance_tax_keywords):
            return 'DEBIT'

        # DÉTECTION DES SOLDES (BALANCE) - Dernière priorité
        balance_keywords = ['SOLDE', 'SOLDE COMPTE', 'SOLDE DISPONIBLE', 'BALANCE', 'AVAILABLE BALANCE', 'NOUVEAU SOLDE']
        if any(word in normalized_upper for word in balance_keywords):
            # Vérifier que ce n'est pas une transaction avec solde
            has_transaction = (
                re.search(r'[CD]\s+\d', normalized_upper) or
                any(word in normalized_upper for word in debit_keywords + credit_keywords + fee_keywords + loan_keywords) or
                'PAIEMENT' in normalized_upper or
                'RETRAIT' in normalized_upper or
                'VERSEMENT' in normalized_upper or
                'SGCNCT' in normalized_upper
            )
            if not has_transaction:
                return 'BALANCE'

        # ✅ AJOUT : Log pour les SMS non classifiés
        logger.warning(f"⚠️ SMS non classifié: {normalized_body[:100]}...")
        return 'UNKNOWN'