
"""
Classe de base pour tous les extracteurs
"""

from abc import ABC, abstractmethod
from utils.logger import setup_logger

logger = setup_logger()

class BaseExtractor(ABC):
    """Classe abstraite de base pour tous les extracteurs"""
    
    def __init__(self):
        self.patterns = []
        self._compile_patterns()
    
    @abstractmethod
    def _compile_patterns(self):
        """Méthode abstraite pour compiler les patterns regex"""
        pass
    
    @abstractmethod
    def extract(self, normalized_body):
        """Méthode abstraite pour extraire les données"""
        pass
    
    def _safe_extract(self, normalized_body, extract_method):
        """Méthode sécurisée pour l'extraction avec gestion d'erreurs"""
        try:
            return extract_method(normalized_body)
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction: {e}")
            return None
    
    def _search_patterns(self, normalized_body, patterns):
        """Recherche dans les patterns avec gestion d'erreurs"""
        for pattern in patterns:
            try:
                match = pattern.search(normalized_body)
                if match:
                    return match
            except Exception as e:
                logger.warning(f"Erreur avec le pattern {pattern}: {e}")
                continue
        return None