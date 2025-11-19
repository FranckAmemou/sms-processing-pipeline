

import re

from core.parsers import parse_currency_amount
def extract_amount(normalized_body):
    """Extrait le montant de la transaction - VERSION COMPLÈTE ET FONCTIONNELLE"""
    patterns = [
        r'XOF\s+([\d\.,]+)\s+D[ÉE]BIT',
        r'XOF\s+([\d\.,]+)\s+Debit',
        r'XOF\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+',
                # Pattern pour "jusqu'à 300.000 F"
        r'JUSQU.A\s+([\d\s.,]+)\s*F',
        r'JUSQU.A\s+([\d\s.,]+)\s*FCFA',
        r'RECEVEZ\s+JUSQU.A\s+([\d\s.,]+)\s*F',
        r'RECEVEZ\s+JUSQU.A\s+([\d\s.,]+)\s*FCFA',
                # NOUVEAUX PATTERNS pour prêt accepté
        r'MONTANT NET RECU\s*:\s*([\d\s,]+)\s*FCFA',
        r'MONTANT NET RECU\s*:\s*([\d\s,]+)\s*F',
        r'NET RECU\s*:\s*([\d\s,]+)\s*FCFA',
        r'RECU\s*:\s*([\d\s,]+)\s*FCFA',
                # Patterns pour dotations (montant de la dotation)
        r'COMPTE PRINCIPAL:\s*([\d\s,]+)\s*FCFA',
        r'DOTATION MENSUELLE.*(\d+)\s*FCFA',
                # Patterns pour dotations (montant de la dotation)
        r'COMPTE PRINCIPAL:\s*([\d\s,]+)\s*FCFA',
        r'DOTATION MENSUELLE.*(\d+)\s*FCFA',
         # NOUVEAUX PATTERNS pour format Orange Money avec "F"
        r'MONTANT PAIEMENT EFFECTUE:\s*([\d\.,]+)F',
        r'MONTANT PAIEMENT EFFECTUE\s*:\s*([\d\.,]+)F',
        r'PAIEMENT EFFECTUE\s*:\s*([\d\.,]+)F',
        r'MONTANT\s*:\s*([\d\.,]+)F',
        r'(\d+\.\d+)F(?=\s|\.|$)',  # Format: 10100.00F
        r'(\d+,\d+)F(?=\s|\.|$)',   # Format: 10100,00F
        # Pattern pour "Transfert d argent de X FCFA recu"
        r'TRANSFERT D ARGENT DE\s+([\d\s,\.]+)\s*FCFA\s+RECU',
        r'TRANSFERT D\'ARGENT DE\s+([\d\s,\.]+)\s*FCFA\s+RECU',
        r'TRANSFERT DE\s+([\d\s,\.]+)\s*FCFA\s+RECU',
        # Pattern amélioré pour remboursements
        r'REMBOURSEMENT DE\s+([\d\s,]+)\s*FCFA',
        r'REMBOURSEMENT DE\s+(\d+)\s*FCFA',
        r'REMBOURSEMENT\s+DE\s+([\d\s]+)\s*FCFA',

        #  Pattern plus large pour capturer "remboursement de 1000 FCFA"
        r'REMBOURSEMENT[^\d]*([\d\s,]+)\s*FCFA',
        r'REMBOURSEMENT[^\d]*(\d[\d\s]*)\s*FCFA',
        r'EPARGNE A ETE DEBITE DE\s+([\d\s]+)\s*FCFA',
        r'DEBITE DE\s+([\d\s]+)\s*FCFA.*EPARGNE',
        r'EPARGNE.*DEBITE.*?(\d+)\s*FCFA'
        r'XOF\s+([\d\.,]+)',  # "XOF 4,00"
        r'DEBITE DE XOF\s+([\d\.,]+)',  # "débité de XOF 4,00"
        r'DEBITE DE\s+XOF\s+([\d\.,]+)',
        r'DEBITEE? DE\s+([\d\.,]+)\s+XOF',
        r'DEBIT\s+DE\s+([\d\.,]+)\s+XOF'
        r'VOUS AVEZ RECU\s+([\d\.,]+)F\s+DE',
        r'RECU\s+([\d\.,]+)F\s+DE',
        r'AVEZ RECU\s+([\d\.,]+)F\s+DE',
        # Pattern pour format avec point décimal "27.300F"
        r'RECU\s+(\d+\.\d+)F',
        r'RECU\s+(\d+\,\d+)F',
        r'RECU\s+(\d+)F',
        # Pattern pour rechargement TresorMoney
        r'RECHARGEMENT DE ORANGE MONEY VERS TRESORMONEY EFFECTUE AVEC SUCCES\. MONTANT:\s*([\d\s]+)\s*FRS',
        r'MONTANT:\s*([\d\s]+)\s*FRS\. REFERENCE:',
        r'MONTANT:\s*([\d\s,]+)\s*FRS',
        r'S\'ELEVENT A\s+(\d+)\s*FCFA',
        r'ELEVENT A\s+(\d+)\s*FCFA',
        r'A\s+(\d+)\s*FCFA.*INTERETS',
        #  Pattern pour transfert automatique vers épargne
        r'TRANSFERT AUTOMATIQUE DE\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERT AUTOMATIQUE DE\s+([\d\s,]+)\s*F',
        r'AUTOMATIQUE DE\s+([\d\s,]+)\s*FCFA',
        #  Patterns pour Facebook USD
        r'PAIEMENT DE\s+([\d\s,\.]+)\s+USD\s+CHEZ FACEBK',
        r'PAIEMENT DE\s+([\d\s,\.]+)\s+USD\s+CHEZ',
        r'PAIEMENT DE\s+([\d\s,\.]+)\s+USD',
        r'YOUR PAYMENT OF\s+([\d\s,\.]+)\s+USD\s+AT',
        r'PAYMENT OF\s+([\d\s,\.]+)\s+USD\s+AT',
        #  Pattern pour transfert international Orange Money
        r'TRANSFERT D ARGENT REUSSI DE\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERT D\'ARGENT REUSSI DE\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERT REUSSI DE\s+([\d\s,]+)\s*FCFA',
        #Patterns pour transferts Orange Bank vers Orange Money
        r'TRANSFERT DE\s+([\d\s,]+)\s*FCFA\s+VERS.*ORANGE MONEY',
        r'TRANSFERT DE\s+([\d\s,]+)\s*FCFA.*VOTRE COMPTE ORANGE MONEY',
        r'VOTRE TRANSFERT DE\s+([\d\s,]+)\s*FCFA.*ORANGE MONEY',
         # Pattern pour "Un retrait de X FCFA" avec espaces
        r'UN RETRAIT DE\s+([\d\s]+)\s*FCFA',
        r'RETRAIT DE\s+([\d\s]+)\s*FCFA',
        r'RETRAIT\s+([\d\s]+)\s*FCFA',
       #  Pattern pour "Un depot de X FCFA" avec espaces
        r'UN DEPOT DE\s+([\d\s]+)\s*FCFA',
        r'DEPOT DE\s+([\d\s]+)\s*FCFA',
        r'DEPOT\s+([\d\s]+)\s*FCFA',
         #  Achats de crédit
        r'VOUS AVEZ ACHETE\s+([\d\s]+)\s*FCFA\s+DE CREDIT',
        r'ACHETE\s+([\d\s]+)\s*FCFA\s+DE CREDIT',
        r'ACHAT DE\s+([\d\s]+)\s*FCFA\s+DE CREDIT',
        r'CREDIT DE COMMUNICATION\s+([\d\s]+)\s*FCFA',
        #  Patterns pour paiements (HAUTE PRIORITÉ)
        r'VOUS AVEZ PAYE\s+([\d\s,]+)\s*FCFA\s+A',
        r'PAYE\s+([\d\s,]+)\s*FCFA\s+A',
        r'VOUS AVEZ PAYE\s+([\d\s,]+)\s*FCFA',
        # Patterns pour réceptions (HAUTE PRIORITÉ)
        r'VOUS AVEZ RECU\s+([\d\.,]+)\s*FCFA\s+DE',
        r'RECU\s+([\d\.,]+)\s*FCFA\s+DE',
        r'AVEZ RECU\s+([\d\.,]+)\s*FCFA',
        r'RECU\s+(\d+\.\d+)\s*FCFA',
        r'RECU\s+(\d+\,\d+)\s*FCFA',
        r'RECU\s+(\d+)\s*FCFA',
        # Pattern spécifique pour Moov Money "Vous avez payé X FCFA au marchand"
        r'VOUS AVEZ PAYE\s+(\d+)\s*FCFA\s+AU MARCHAND',
        r'PAYE\s+(\d+)\s*FCFA\s+AU MARCHAND',
        r'PAYE\s+([\d\s,]+)\s*FCFA\s+AU MARCHAND',
        #  Pattern amélioré pour "Vous avez envoye X.XX FCFA"
        r'VOUS AVEZ ENVOYE\s+([\d\s,\.]+)\s*FCFA',
        r'ENVOYE\s+([\d\s,\.]+)\s*FCFA',
        r'AVEZ ENVOYE\s+([\d\s,\.]+)\s*FCFA',
        # Pattern pour "Vous avez envoye X FCFA"
        r'VOUS AVEZ ENVOYE\s+([\d\s,]+)\s*FCFA',
        r'ENVOYE\s+([\d\s,]+)\s*FCFA',
        r'AVEZ ENVOYE\s+([\d\s,]+)\s*FCFA',
        #  Pattern spécifique pour transfert GIMAC
        r'TRANSFERT GIMAC DE\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERT GIMAC\s+([\d\s,]+)\s*FCFA',
        r'GIMAC DE\s+([\d\s,]+)\s*FCFA',
        # Pattern pour "transfert de 9200FCFA" (sans espace)
        r'TRANSFERT DE\s+(\d+)FCFA',
        r'TRANSFERT DE\s+(\d+)\s*FCFA',
        r'TRANSFERT DE\s+([\d\s,]+)FCFA',
        r'TRANSFERT DE\s+([\d\s,]+)\s*FCFA',
        r'RECU UN TRANSFERT DE\s+(\d+)\s*FCFA',
        r'AVEZ RECU UN TRANSFERT DE\s+(\d+)\s*FCFA',
        # Pattern pour "Paiement effectue pour 995 FCFA"
        r'PAIEMENT EFFECTUE POUR\s+(\d+)\s*FCFA',
        r'PAIEMENT EFFECTUE POUR\s+([\d\s,]+)\s*FCFA',
        r'PAIEMENT EFFECTUE\s+(\d+)\s*FCFA',
        r'PAIEMENT\s+(\d+)\s*FCFA\s+A\s+',
      #  Pattern pour "une somme 2000 FCFA"
        r'UNE SOMME\s+(\d+)\s*FCFA',
        r'UNE SOMME\s+([\d\s,]+)\s*FCFA',
        r'SOMME\s+(\d+)\s*FCFA',
        r'SOMME\s+([\d\s,]+)\s*FCFA',

        # Patterns pour retraits
        r'AVEZ RETIRE.*SOMME\s+(\d+)\s*FCFA',
        r'RETIRE.*SOMME\s+(\d+)\s*FCFA',
        # Pattern pour "Transfert 61000F a"
        r'TRANSFERT\s+(\d+)\s*F\s+A\s+',
        r'TRANSFERT\s+(\d+)\s*F\s+',
        r'TRANSFERT\s+(\d+)\s*FCFA\s+A\s+',
        r'TRANSFERT\s+([\d\s,]+)\s*F\s+A\s+',
        # Pattern pour "Transfert effectue pour 10000 FCFA"
        r'TRANSFERT EFFECTUE POUR\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERT EFFECTUE POUR\s+(\d+)\s*FCFA',
        r'TRANSFERT EFFECTUE\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERT\s+([\d\s,]+)\s*FCFA',
        #Pattern pour "Depot recu 1200F de"
        r'DEPOT RECU\s+(\d+)\s*F\s+DE',
        r'DEPOT\s+RECU\s+(\d+)\s*F',
        r'RECU\s+(\d+)\s*F\s+DE',
        r'DEPOT\s+DE\s+(\d+)\s*F',
        #  Pattern spécifique pour "Paiement 500F a MTN BUNDLES"
        r'PAIEMENT\s+(\d+)\s*F\s+A\s+',
        r'PAIEMENT\s+(\d+)\s*F\s+',
        r'PAIEMENT\s+DE\s+(\d+)\s*F',
        r'PAIEMENT\s+(\d+)\s*FCFA',
        #Pattern pour retraits chez le marchand (HAUTE PRIORITÉ)
        r'VOUS AVEZ RETIRE\s+(\d[\d\s,]*)\s*FCFA\s+DE VOTRE COMPTE',
        r'RETIRE\s+(\d[\d\s,]*)\s*FCFA\s+DE VOTRE COMPTE',
        r'VOUS AVEZ RETIRE\s+(\d[\d\s,]*)\s*FCFA',
        r'RETIRE\s+(\d[\d\s,]*)\s*FCFA',
        #  Patterns pour recouvrement de dette (HAUTE PRIORITÉ)
        r'FINAL DEBT COLLECTION OF\s+([\d\s,]+)\s*XOF',
        r'DEBT COLLECTION OF\s+([\d\s,]+)\s*XOF',
        r'TOTAL COLLECTED AMOUNT:\s*([\d\s,]+)',
        r'AMOUNT COLLECTED:\s*([\d\s,]+)\s*XOF',
        #  Patterns pour les prêts (HAUTE PRIORITÉ)
        r'PAYOUT OF\s+([\d\s,]+)\s*XOF\s+FOR LOAN',
        r'LOAN AMOUNT:\s*([\d\s,]+)\s*XOF',
        r'AMOUNT:\s*([\d\s,]+)\s*XOF',
        r'DISBURSEMENT OF\s+([\d\s,]+)\s*XOF',
        # Patterns pour transferts MTN MOMO en français
        r'VOUS AVEZ TRANSFERE\s+([\d\s,]+)\s*FCFA',
        r'TRANSFERE\s+([\d\s,]+)\s*FCFA\s+AU',
        r'TRANSFERE\s+([\d\s,]+)\s*FCFA',
        # Pattern pour transferts mobile money en anglais "You have transferred X XOF"
        r'YOU HAVE TRANSFERRED\s+([\d\s,]+)\s*XOF',
        r'TRANSFERRED\s+([\d\s,]+)\s*XOF\s+TO',
        #  Patterns pour paiements MTN MOMO en anglais
        r'PAYMENT OF\s+([\d\s,]+)\s*FCFA.*SUCCESSFULLY',
        r'THE PAYMENT OF\s+([\d\s,]+)\s*FCFA.*SUCCESSFULLY',
        r'PAYMENT OF\s+([\d\s,]+)\s*FCFA',
        #  Patterns pour MTN MOMO
        r'PAIEMENT\s+DE\s+([\d\s,]+)\s*FCFA',
        r'LE PAIEMENT\s+DE\s+([\d\s,]+)\s*FCFA',
        r'PAIEMENT\s+([\d\s,]+)\s*FCFA',
        #  Patterns pour RECEPTION MOBILE MONEY
        r'VOUS AVEZ RECU\s+([\d\s,]+)\s*FCFA',
        r'RECU\s+([\d\s,]+)\s*FCFA\s+DE',
        r'CREDIT\s+DE\s+([\d\s,]+)\s*FCFA',
        r'VIREMENT\s+RECU\s+DE\s+([\d\s,]+)\s*FCFA',
        #  Patterns pour AMOBILE avec capture COMPLÈTE
        r'MONTANT:\s*([\d\s]+)\s*XOF',
        r'MONTANT\s*:\s*([\d\s]+)\s*XOF',
        r'MONTANT\s+([\d\s]+)\s*XOF',
        # Patterns pour BNI ONLINE
        r'SUCCES DU VIREMENT.*MONTANT\s+(\d+)',
        r'MONTANT\s+(\d+)(?=\s+Attention)',
        r'VIREMENT.*MONTANT\s+(\d+)',
        #  Patterns pour TRANSFERTS SORTANTS FLOOZ
        r'TRANSFERT VERS.*REUSSI.*MONTANT:\s*([\d\s,]+)\s*FCFA',
        r'MONTANT:\s*([\d\s,]+)\s*FCFA.*TRANSFERT VERS',

        #  Patterns pour TRANSFERTS INTERNATIONAUX FLOOZ
        r'TRANSFERT INTERNATIONAL RECU\s+MONTANT:\s*([\d\s,]+)\s*FCFA',
        r'MONTANT:\s*([\d\s,]+)\s*FCFA.*TRANSFERT INTERNATIONAL',

        # Patterns génériques FLOOZ avec MONTANT:
        r'MONTANT:\s*([\d\s,]+)\s*FCFA',

        # Patterns spécifiques FLOOZ
        r'RETRAIT VALIDE\s+MONTANT:\s*([\d\s,]+)\s*FCFA',
        r'MONTANT:\s*([\d\s,]+)\s*FCFA.*RETRAIT',
        r'MONTANT\s*:\s*([\d\s,]+)\s*FCFA',

        # Pattern pour crédits "TEXTE VARIABLE C MONTANT"
        r'C\s+([\d\s.,]+)(?=\s|\.|$|nouveau|Nouveau|NOUVEAU|solde|Solde|SOLDE)',
        r'C\s+([\d\s.,]+)\s*(?:nouveau solde|NOUVEAU SOLDE|solde|SOLDE)',
        r'C\s+([\d\s.,]+)',

        # Pattern générique pour "TEXTE VARIABLE D MONTANT"
        r'D\s+([\d\s.,]+)(?=\s|\.|$|nouveau|Nouveau|NOUVEAU|solde|Solde|SOLDE)',
        r'D\s+([\d\s.,]+)\s*(?:nouveau solde|NOUVEAU SOLDE|solde|SOLDE)',
        r'D\s+([\d\s.,]+)',

        # Pattern pour "RETRAIT DAB D 200000" (espace entre D et le montant)
        r'RETRAIT DAB\s+D\s*([\d\s.,]+)',
        r'RETRAIT DAB\s+D\s*([\d\s.,]+)(?=\s|\.|$)',
        r'RETRAIT DAB[:\s]*D\s*([\d\s.,]+)',

        # Pattern pour "RETRAIT DAB - ON LINE D 200000"
        r'RETRAIT DAB[^D]*D\s*([\d\s.,]+)',
        r'RETRAIT[^D]*D\s*([\d\s.,]+)',

        #Pattern pour "PRELEVEMENT D 9700" (espace entre D et le montant)
        r'PRELEVEMENT\s+D\s*([\d\s.,]+)',
        r'PRELEVEMENT\s+D\s*([\d\s.,]+)(?=\s|\.|$)',
        r'PRELEVEMENT[:\s]*D\s*([\d\s.,]+)',

        #  Pattern pour "DEBIT D 9700"
        r'DEBIT\s+D\s*([\d\s.,]+)',
        r'DEBIT[:\s]*D\s*([\d\s.,]+)',

        # Pattern pour "PAIEMENT DE X XOF PAR CARTE"
        r'PAIEMENT DE\s*([\d\s.,]+)\s*XOF PAR CARTE',
        r'PAIEMENT\s*DE\s*([\d\s.,]+)\s*XOF\s*PAR',

        # Patterns existants
        r'RETRAIT DE\s*([\d\s.,]+)\s*XOF PAR LA CARTE',

        # Pattern pour "RETRAIT DE X XOF PAR LA CARTE"
        r'RETRAIT DE\s*([\d\s.,]+)\s*XOF PAR LA CARTE',
        r'RETRAIT DE\s*([\d\s.,]+)\s*XOF\s*PAR',

        # Patterns existants pour retraits
        r'RETRAIT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',

        # Pattern pour format multi-opérations "06/08 -4180 PACK ESSENTIEL"
        r'\d{1,2}/\d{1,2}\s+-(\d+)\s+[A-Z]',
        r'\d{1,2}/\d{1,2}\s+-(\d+)\s+PACK',
        r'\d{1,2}/\d{1,2}\s+-(\d+)\s+AGIOS',

        #  Pattern pour format "Alerte Debit: 770000.00 FCFA" avec décimales
        r'Alerte Debit:\s*([\d\s.,]+\.[\d]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'ALERTE DEBIT:\s*([\d\s.,]+\.[\d]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'Debit:\s*([\d\s.,]+\.[\d]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'DEBIT:\s*([\d\s.,]+\.[\d]+)\s*(?:FCFA|XOF|USD|EUR)',

        #  Pattern spécifique pour CORIS "de XOF 77000"
        r'de XOF\s+(\d+)',
        r'DE XOF\s+(\d+)',
        r'XOF\s+(\d+)\s+au debit',
        r'XOF\s+(\d+)\s+AU DEBIT',

        # NOUVEAU : Pattern spécifique CORIS "Montant: 130290.0"
        r'Montant:\s*([\d\.,]+)',
        r'MONTANT:\s*([\d\.,]+)',
        r'Montant\s*:\s*([\d\.,]+)',
        r'MONTANT\s*:\s*([\d\.,]+)',

        # NOUVEAU : Pattern spécifique pour "un virement de 1.565.100 F"
        r'un virement de\s*([\d\s.,.]+)\s*F',
        r'UN VIREMENT DE\s*([\d\s.,.]+)\s*F',
        r'au credit.*un virement de\s*([\d\s.,.]+)\s*F',
        r'AU CREDIT.*UN VIREMENT DE\s*([\d\s.,.]+)\s*F',

        # NOUVEAU : Pattern général pour montant suivi de "F"
        r'de\s*([\d\s.,.]+)\s*F\.',
        r'DE\s*([\d\s.,.]+)\s*F\.',

        # NOUVEAU : Pattern spécifique BRIDGE BANK "MONTANT : 184,925"
        r'MONTANT\s*:\s*([\d\s.,]+)(?=,|$)',
        r'MONTANT\s*:\s*([\d\s.,]+)\s*,\s*DATE',
        r'MONTANT\s*:\s*([\d\s.,]+)(?=\s*DATE)',

        # NOUVEAU : Pattern spécifique pour Bridge Bank "XOF :-945.000"
        r'XOF\s*:\s*-?([\d\s.,]+)\s*,\s*Le solde',
        r'XOF\s*:\s*-?([\d\s.,]+)(?=,Le solde|,LE SOLDE)',
        r'de XOF\s*:\s*-?([\d\s.,]+)',

        # NOUVEAU : Pattern pour virements émis avec format négatif
        r'Virements emis.*XOF\s*:\s*-?([\d\s.,]+)',
        r'VIREMENTS EMIS.*XOF\s*:\s*-?([\d\s.,]+)',

        # NOUVEAUX PATTERNS POUR VOTRE FORMAT
        r'retrait guichet de\s*([\d\s.,]+)\s*F',
        r'RETRAIT GUICHET DE\s*([\d\s.,]+)\s*F',
        r'un retrait guichet de\s*([\d\s.,]+)\s*F',
        r'UN RETRAIT GUICHET DE\s*([\d\s.,]+)\s*F',

        # Pattern spécifique pour BICICI avec format "Montant : X XXX FCFA"
        r'Montant\s*:\s*([\d\s,]+)\s*FCFA',
        r'MONTANT\s*:\s*([\d\s,]+)\s*FCFA',
        r'Montant\s*:\s*([\d\s,]+)\s*XOF',
        r'MONTANT\s*:\s*([\d\s,]+)\s*XOF',

        # CORRECTION : Pattern pour dépôts en premier
        r'DEPOSER\s*(?:XOF|FCFA|USD|EUR)?\s*([-]?\s*[\d\s.,]+)',
        r'DEPOT\s*(?:XOF|FCFA|USD|EUR)?\s*([-]?\s*[\d\s.,]+)',
        r'VERSEMENT\s*(?:XOF|FCFA|USD|EUR)?\s*([-]?\s*[\d\s.,]+)',

        # Patterns français
        r'DEBITE? DE?[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'DEBIT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'DEBITE[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'MONTANT DEBITE[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'RETRAIT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'RETIRE[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',

        # Patterns avec devise avant le montant (priorité haute)
        r'^(?:XOF|FCFA|USD|EUR)\s*([\d\s.,]+)',
        r'(?:XOF|FCFA|USD|EUR)\s*([\d\s.,]+)(?=\s|\.|$)',

        #  Pattern spécifique pour "XOF58,100" (sans espace)
        r'(?:XOF|FCFA|USD|EUR)([\d\s.,]+)(?=\s|\.|,)',

        # Patterns génériques
        r'CREDITE? DE?[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'CREDIT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'VIREMENT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'MONTANT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'MONTANT\s+DE[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'TRANSACTION[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'PAIEMENT[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'D\'UN MONTANT DE[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)',
        r'VOUS AVEZ RETIRE[:\s]*([-]?\s*[\d\s.,]+)\s*(?:FCFA|XOF|USD|EUR)'
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_body, re.IGNORECASE)
        if match:
            amount_str = match.group(1).strip()
            amount_str = re.sub(r'\s*-\s*', '-', amount_str)
            amount = parse_currency_amount(amount_str)
            if amount is not None and amount != 0.0:

                return amount


    return None
