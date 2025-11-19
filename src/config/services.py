"""
Configuration des services autorisés et mots-clés
"""

# Services autorisés
SERVICE_NAME_USED = [
    'Info Orange', 'Tik Tak', 'OrangeMoney', 'WITTI CI', 'WAVE CI', 'MOOVMONEY',
    'SanlamAZvie', 'FastPay', 'TaptapSend', 'MoMo', 'TresorMoney', 'MTN CI',
    'MobileMoney', 'OrangeMoney', 'CORIS', 'ORANGE BANK', 'VERSUS BANK',
    'BANK-TRESOR', 'BICICI SMS', 'BRIDGE BANK', 'BNI-ONLINE', 'ECOBANK',
    'GTBank CI', 'INFOS', 'MOOV MONEY', 'Moov Money', 'MoovMoney', 'MOOVMONEY',
    'PUSH CI', 'SIB', 'SocGen', 'AFGMOBILE', 'SanlamAZvie', 'MOOV CREDIT',
    'Depot MoMo', 'AFGMOBILE'
]

# Mots-clés à ignorer
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
    'belles fetes','confirmez le paiement','DEVINETTE','TRANSPORT EN COMMUN','LA COMPOSITION','QUIPUX LE','Le saviez-vous ',
    'de gigas!','Infos sous comptes','Le montant recharge est de','EST PRÊT POUR LE RETRAIT',
    'La HomeBox','PARTAGE AVEC MTN','Transférez gratuitement','Avec QUIZ REVISION','INFOS BRVM','A ne pas rater!',
    'jours de bonheur','Weekend surprise','fun','votre identification a été validée','Félicitations','pr?t f?tes','Application Ecobank Mobile',
    'Application Ecobank Mobile','Application Ecobank Mobile','vos operations Ecobank Mobile','informations bancaires'
]

# Senders à toujours ignorer
ALWAYS_IGNORE_SENDERS = [
    'INFOS BRVM', 'BRVM', 'INFO BRVM', 'BVRM',
    'PROMOTION', 'PUB', 'PUBLICITE', 'MARKETING'
]