"""
Configuration des services et mots-clés
"""

# Liste des services autorisés (tous les autres seront ignorés)
SERVICE_NAME_USED = [
    'Tik Tak', 'OrangeMoney', 'WITTI CI', 'WAVE CI', 'MOOVMONEY', 'SanlamAZvie', 
    'FastPay', 'TaptapSend', 'MoMo', 'TresorMoney', 'MTN CI', 'MobileMoney', 
    'OrangeMoney', 'CORIS', 'ORANGE BANK', 'VERSUS BANK', 'BANK-TRESOR', 
    'BICICI SMS', 'BRIDGE BANK', 'BNI-ONLINE', 'ECOBANK', 'GTBank CI', 
    'INFOS', 'MOOV MONEY', 'Moov Money', 'MoovMoney', 'MOOVMONEY', 'PUSH CI', 
    'SIB', 'SocGen'
]

# Mots-clés à ignorer (uniquement pour les services autorisés)
IGNORE_KEYWORDS = [
    "promotion", "recrutement", "cliquez", "gagnez", "profitez", "cadeau", "concours",
    "ECHEC", "Tarifs", "CEET", "Y'ello", "Pour valider", "Bienvenue", "OTP",
    "Your one time", "terminant par", "Veuillez saisir", "en cours de traitement",
    "echoue ", "Welcome", "du cashback2.sp", "a echoue", "Decolle avec",
    "code de retrait", "expire dans", "veuillez utiliser", "pour retirer",
    "retrait code", "code expire", "utiliser le code", "auprès de tout point",
    "tentez de gagner", "clique et gagne", "jeu moov money", "lots en participant",
    "faites vos transactions", "voyage au maroc", "télévisions"," l'élève de matricule",
    'Réalise ta 1ere transaction', 'Reabonnement reussi','Abonnement CANAL','recharger vos coffres-forts',
    'Go à la 1ère facture payée','illimix semaine','500B!GB!CFA','Promo Flash','Card has expired','SUPER!',
    'belles fetes','confirmez le paiement','DEVINETTE','TRANSPORT EN COMMU','LA COMPOSITION','QUIPUX LE','Le saviez-vous ',
    'de gigas!','retard','Infos sous comptes','Le montant recharge est de','EST PRÊT POUR LE RETRAIT',
    'La HomeBox','PARTAGE AVEC MTN'
]

# Mapping des labels de transaction
TRANSACTION_LABELS = {
    'INCOMING_TRANSFER': [
        'INCOMING TRANSFER', 'VIREMENT RECU', 'TRANSFERT RECU', 'CREDIT'
    ],
    'OUTGOING_TRANSFER': [
        'OUTGOING TRANSFER', 'VIREMENT EFFECTUE', 'TRANSFERT EFFECTUE', 'DEBIT'
    ],
    'CASH_OPERATIONS': [
        'CASH DEPOSIT', 'CASH WITHDRAWAL', 'RETRAIT', 'DEPOT'
    ],
    'PURCHASES': [
        'PURCHASE', 'ACHAT', 'PAIEMENT', 'ONLINE PAYMENT'
    ],
    'FEES': [
        'BANK FEES', 'FEES', 'COMMISSION', 'FRAIS'
    ],
    'LOANS': [
        'LOAN REPAYMENT', 'LOAN DISBURSEMENT', 'PRET'
    ]
}