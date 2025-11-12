import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # S3 Configuration
    S3_BUCKET = os.getenv('S3_BUCKET', 'civ-production-sentinel-snapshots')
    S3_KEY = os.getenv('S3_KEY', '2025_07_30/client_8ea23811-ba1c-4a1c-a59e-ecb1f4b8360f/device_4f5a4e67259d8483/12_20_57_033.csv')
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # BigQuery Configuration
    BIGQUERY_PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID', 'your-project-id')
    BIGQUERY_CREDENTIALS_PATH = os.getenv('BIGQUERY_CREDENTIALS_PATH', './credentials/bigquery-credentials.json')
    
    # Application Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
