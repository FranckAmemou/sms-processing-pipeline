import logging
import sys
import os
from datetime import datetime

def setup_logger(name=None, level=logging.INFO, log_file=None):
    """
    Configure et retourne un logger
    """
    # Créer le logger
    logger = logging.getLogger(name or 'sms_pipeline')
    logger.setLevel(level)
    
    # Éviter les handlers dupliqués
    if logger.handlers:
        logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier (si spécifié)
    if log_file:
        # Créer le répertoire si nécessaire
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger par défaut
logger = setup_logger()