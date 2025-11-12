class AccountClassifier:
    def classify(self, row, normalized_body, transaction_type, label):
        """
        Détermine le type de compte - VERSION COMPLÈTE
        """
        normalized_upper = normalized_body.upper()

        # ACCÈS DIRECT au Sender ID depuis la row du CSV
        sender_name = str(row.get('Sender ID', '')).upper()

        # VÉRIFICATION COMPTE ÉPARGNE (SAVINGS ACCOUNT)
        savings_indicators = [
            'LE SOLDE DE VOTRE EPARGNE',
            'SOLDE EPARGNE',
            'VOTRE EPARGNE A ETE DEBITE',
            'COMPTE D\'EPARGNE',
            'SOLDE D\'EPARGNE',
            'EPARGNE GELES',
            'EPARGNE GELEES'
        ]

        for phrase in savings_indicators:
            if phrase in normalized_upper:
                return "SAVINGS ACCOUNT"

        # VÉRIFICATION COMPTE MOBILE (MOBILE ACCOUNT)
        mobile_money_senders = [
            'ORANGEMONEY', 'ORANGE MONEY', 'ORANGE-MONEY', 'ORANGEMONY',
            'MOOV MONEY', 'MOOVMONEY', 'MOOV',
            'MTN MONEY', 'MTNMONEY', 'MTN MOMO', 'MTN',
            'FLOOZ', 'FLOOZ CI', 'FLOOZCI',
            'TIKTAK', 'WAVE', 'YUP', 'CINAR', 'JONA',
            '2SICASH', '2SI CASH', 'ECOBANK MOMO', 'ECOBANK-MOMO',
            'WAVE CI', 'MOBILEMONEY', 'MOBILE MONEY'
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
            'VIA OM', 'PAR OM', 'COMPTE OM', 'SOLDE ORANGE MONEY',
            'VOTRE SOLDE MOOV MONEY', 'SOLDE FLOOZ',
            'COMPTE PRINCIPAL FLOOZ', 'WALLET',
            'PORTEFEUILLE', 'E-WALLET'
        ]

        for phrase in mobile_money_content:
            if phrase in normalized_upper:
                return "MOBILE ACCOUNT"

        # Détection spécifique pour les comptes épargne Orange Bank
        if ('ORANGE BANK' in normalized_upper and 
            any(word in normalized_upper for word in ['EPARGNE', 'SAVINGS', 'EPARNE'])):
            return "SAVINGS ACCOUNT"

        # Détection des comptes courants avec indicateurs spécifiques
        current_account_indicators = [
            'COMPTE COURANT', 'CURRENT ACCOUNT', 'COMPTE CHÈQUE', 'CHECKING ACCOUNT',
            'SOLDE COMPTE', 'COMPTE BANCAIRE', 'BANK ACCOUNT',
            'VIREMENT', 'TRANSFERT', 'RETRAIT DAB', 'CARTE BANCAIRE'
        ]

        for phrase in current_account_indicators:
            if phrase in normalized_upper:
                return "CURRENT ACCOUNT"

        # COMPTE COURANT (CURRENT ACCOUNT) - PAR DÉFAUT
        # Si on arrive ici et que c'est une banque traditionnelle, c'est un compte courant
        traditional_banks = [
            'CORIS', 'ORANGE BANK', 'VERSUS BANK', 'BANK-TRESOR', 'BICICI SMS', 
            'BRIDGE BANK', 'BNI-ONLINE', 'ECOBANK', 'GTBank CI', 'SIB', 'SocGen',
            'NSIA', 'ORABANK', 'SGBCI', 'BIAO', 'BANQUE ATLANTIQUE'
        ]

        if sender_name:
            for bank in traditional_banks:
                if bank in sender_name:
                    return "CURRENT ACCOUNT"

        # Fallback basé sur le type de transaction
        if transaction_type in ['BALANCE', 'LOAN', 'UNKNOWN']:
            return "CURRENT ACCOUNT"

        # Dernier fallback
        return "CURRENT ACCOUNT"