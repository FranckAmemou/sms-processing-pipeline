"""
Client S3 pour charger les données depuis AWS
"""

import pandas as pd
import io
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from utils.logger import setup_logger

logger = setup_logger()

def load_csv_from_s3(bucket_name, key, aws_access_key_id=None, aws_secret_access_key=None, region_name='us-east-1'):
    """
    Charge un fichier CSV depuis Amazon S3
    """
    try:
        # Initialiser le client S3
        if aws_access_key_id and aws_secret_access_key:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            # Utiliser les credentials par défaut (IAM roles, environment variables, etc.)
            s3_client = boto3.client('s3')

        # Télécharger le fichier depuis S3
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        csv_content = response['Body'].read().decode('utf-8')

        # Charger dans un DataFrame pandas
        df = pd.read_csv(io.StringIO(csv_content))

        logger.info(f"Fichier chargé depuis S3: {bucket_name}/{key}")
        logger.info(f"   Shape: {df.shape}")

        return df

    except NoCredentialsError:
        logger.error("Erreur: Aucune credential AWS trouvée")
        return None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            logger.error(f"Erreur: Fichier non trouvé dans S3 - {bucket_name}/{key}")
        elif error_code == 'AccessDenied':
            logger.error("Erreur: Accès refusé au bucket S3")
        else:
            logger.error(f"Erreur S3: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement S3: {e}")
        return None