"""
Normalisation du texte des SMS
"""

import re

def normalize_sms(body):
    """
    Normalise le SMS pour un traitement uniforme
    """
    if not isinstance(body, str):
        body = str(body)

    # Convertir en majuscules
    body = body.upper()

    # Normaliser les caractères accentués
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

    # Normaliser les espaces
    body = re.sub(r'\s+', ' ', body).strip()

    return body