"""
Point d'entrée principal du pipeline SMS
"""

import pandas as pd
import sys
import os

# Ajouter le chemin actuel au PYTHONPATH pour les imports relatifs
sys.path.append(os.path.dirname(__file__))

from core.s3_client import load_csv_from_s3
from processors.sms_processor import process_sms
from utils.logger import setup_logger

logger = setup_logger()

def extract_transactions(s3_bucket, s3_key, aws_access_key_id=None, aws_secret_access_key=None, region_name='us-east-2'):
  
    # Validation des paramètres S3
    if not s3_bucket or not s3_key:
        print("Bucket S3 ou clé non spécifié")
        return pd.DataFrame()

    # Charger les données depuis S3
    df = load_csv_from_s3(s3_bucket, s3_key, aws_access_key_id, aws_secret_access_key)

    # Si le chargement a échoué, retourner un DataFrame vide
    if df is None or df.empty:
        print("Aucune donnée chargée depuis S3")
        return pd.DataFrame()

    # Traiter les SMS avec votre logique existante
    processed_data = []
    ignored_count = 0
    processed_count = 0

    for _, row in df.iterrows():
        try:
            result = process_sms(row, s3_key, s3_bucket)
            print('result:', result)
            if result:
                processed_data.extend(result)
                print('processed_data:', processed_data)
                processed_count += 1
                print('processed_count:', processed_count)
            else:
                ignored_count += 1

        except Exception as e:
            print(f" Erreur traitement SMS: {e}")
            continue

    # Créer le DataFrame final
    result_df = pd.DataFrame(processed_data)

    # Ajouter les métadonnées de source
    result_df['data_source'] = f"s3://{s3_bucket}/{s3_key}"

    # Statistiques
    print(f"\n=== STATISTIQUES DE TRAITEMENT ===")
    print(f"SMS traités: {processed_count}")
    print(f"SMS ignorés: {ignored_count}")
    print(f"Total transactions générées: {len(result_df)}")
    print(f"Total SMS originaux: {len(df)}")

    if len(df) > 0:
        print(f"Taux de traitement: {processed_count/len(df)*100:.1f}%")

    return result_df

if __name__ == "__main__":
    # Exemple d'utilisation
    result = extract_transactions(
        s3_bucket="civ-production-sentinel-snapshots",
        s3_key="2025_07_30/client_8ea23811-ba1c-4a1c-a59e-ecb1f4b8360f/device_4f5a4e67259d8483/12_20_57_033.csv"
    )
    print(f"Résultats: {len(result)} transactions extraites")