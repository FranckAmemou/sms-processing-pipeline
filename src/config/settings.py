"""
Configuration globale de l'application
"""

from datetime import datetime

# Configuration S3
S3_BUCKET = "civ-production-sentinel-snapshots"
S3_KEY = "2025_07_30/client_8ea23811-ba1c-4a1c-a59e-ecb1f4b8360f/device_4f5a4e67259d8483/12_20_57_033.csv"

# Paramètres de traitement
DEFAULT_CURRENCY = 'XOF'
SUPPORTED_CURRENCIES = ['XOF', 'USD', 'EUR', 'FCFA','F']
# PROCESSING_DATE_FORMAT = '%Y-%m-%d'


