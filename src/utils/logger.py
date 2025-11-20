
"""
Configuration du logging
"""

import logging

def setup_logger(name=__name__, level=logging.INFO):
    """Configure et retourne un logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger
# Alias pour la compatibilité avec les imports existants
get_logger = setup_logger