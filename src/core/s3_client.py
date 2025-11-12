# src/core/s3_client.py - VERSION RÉELLE UNIQUEMENT
import pandas as pd
import io
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from utils.logger import setup_logger

logger = setup_logger()

def load_csv_from_s3(bucket_name, key, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Charge depuis S3 - Version production réelle
    """
    try:
        # Connexion S3 réelle
        logger.info(f"🔗 Connexion à S3: {bucket_name}/{key}")
        
        if aws_access_key_id and aws_secret_access_key:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            logger.info("✅ Utilisation des credentials AWS fournis")
        else:
            s3_client = boto3.client('s3')
            logger.info("✅ Utilisation des credentials AWS par défaut")

        # Téléchargement du fichier
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        
        logger.info(f"✅ Fichier CSV chargé depuis S3: {bucket_name}/{key}")
        logger.info(f"📊 Données réelles chargées: {len(df)} lignes, {len(df.columns)} colonnes")
        logger.info(f"📋 Colonnes: {list(df.columns)}")
        
        # Aperçu des premières lignes
        if len(df) > 0:
            logger.info(f"👀 Aperçu des données:")
            for i, (_, row) in enumerate(df.head(3).iterrows()):
                logger.info(f"   Ligne {i+1}: {row.get('Sender ID', 'N/A')} - {str(row.get('Body', ''))[:80]}...")
        
        return df

    except NoCredentialsError:
        logger.error("❌ ERREUR CRITIQUE: Aucun credential AWS trouvé")
        raise Exception("Credentials AWS manquants. Configurez AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ ERREUR AWS S3 ({error_code}): {e}")
        raise Exception(f"Erreur S3: {error_code} - {e}")
        
    except Exception as e:
        logger.error(f"❌ ERREUR inattendue: {e}")
        raise Exception(f"Erreur de chargement S3: {e}")


# Fonction utilitaire pour vérifier la connexion S3
def test_s3_connection(bucket_name=None, key=None):
    """
    Teste la connexion S3 - pour diagnostic
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_buckets()
        
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        logger.info(f"✅ Connexion S3 réussie - {len(buckets)} buckets disponibles")
        
        if buckets:
            logger.info(f"📦 Buckets S3: {buckets}")
            
        # Vérifier l'accès au bucket spécifique
        if bucket_name:
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                logger.info(f"✅ Accès confirmé au bucket: {bucket_name}")
                
                if key:
                    # Lister les fichiers dans le bucket pour debug
                    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=key, MaxKeys=5)
                    if 'Contents' in response:
                        files = [obj['Key'] for obj in response['Contents']]
                        logger.info(f"📁 Fichiers trouvés: {files}")
                    
            except ClientError as e:
                logger.error(f"❌ Accès refusé au bucket {bucket_name}: {e}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur de connexion S3: {e}")
        return False