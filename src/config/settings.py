"""
Configuration des paramètres AWS et application
"""

import os

# Configuration AWS - Utiliser les variables d'environnement
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')

# Paramètres S3
S3_BUCKET = os.getenv('S3_BUCKET', 'civ-production-sentinel-snapshots')
S3_PREFIX = os.getenv('S3_PREFIX', '2025_07_30/')

# Paramètres de l'application
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_SMS_LENGTH = int(os.getenv('MAX_SMS_LENGTH', '1000'))