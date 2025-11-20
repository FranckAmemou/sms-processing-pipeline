"""
Script principal pour lancer le pipeline SMS
"""

import sys
import os

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import extract_transactions

def main():
    print("🚀 Démarrage du pipeline de traitement SMS...")
    
    # Configuration AWS via variables d'environnement
    bucket_name = os.getenv('S3_BUCKET', 'civ-production-sentinel-snapshots')
    file_key = os.getenv('S3_KEY', '2025_07_30/client_8ea23811-ba1c-4a1c-a59e-ecb1f4b8360f/device_4f5a4e67259d8483/12_20_57_033.csv')
    
    print(f"📁 Bucket: {bucket_name}")
    print(f"🔑 Clé: {file_key}")
    print("⏳ Traitement en cours...")
    
    try:
        # Extraire les transactions
        results = extract_transactions(
            s3_bucket=bucket_name,
            s3_key=file_key
        )
        
        if not results.empty:
            print(f"✅ Traitement terminé: {len(results)} transactions extraites")
        else:
            print("❌ Aucune transaction extraite")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())