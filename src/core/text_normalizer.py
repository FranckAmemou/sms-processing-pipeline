# src/core/text_normalizer.py
"""
Normalisation du texte des SMS
"""

import re

# ❌ ANCIEN (supprimez cette ligne) :
# from src.utils.logger import setup_logger

# ✅ NOUVEAU (import absolu) :
from utils.logger import setup_logger

logger = setup_logger(__name__)

def normalize_sms(body):
    """
    Normalise le SMS pour un traitement uniforme - FONCTION DIRECTE
    """
    if not isinstance(body, str):
        body = str(body)

    body = body.upper()
    body = body.replace('É', 'E').replace('È', 'E').replace('Ê', 'E').replace('Ë', 'E')
    body = body.replace('À', 'A').replace('Â', 'A').replace('Ä', 'A')
    body = body.replace('Î', 'I').replace('Ï', 'I')
    body = body.replace('Ô', 'O').replace('Ö', 'O')
    body = body.replace('Ù', 'U').replace('Û', 'U').replace('Ü', 'U')
    body = body.replace('Ç', 'C')
    body = body.replace('é', 'E').replace('è', 'E').replace('ê', 'E').replace('ë', 'E')
    body = body.replace('à', 'A').replace('â', 'A').replace('ä', 'A')
    body = body.replace('î', 'I').replace('ï', 'I')
    body = body.replace('ô', 'O').replace('ö', 'O')
    body = body.replace('ù', 'U').replace('û', 'U').replace('ü', 'U')
    body = body.replace('ç', 'C')
    body = re.sub(r'\s+', ' ', body).strip()

    return body

# Vous pouvez garder la classe en option
class TextNormalizer:
    """Normalise le texte des SMS pour un traitement uniforme"""

    @staticmethod
    def normalize_sms(body):
        """Délègue à la fonction principale"""
        return normalize_sms(body)

    @staticmethod
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