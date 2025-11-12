# run_pipeline.py - SCRIPT PRINCIPAL DE PRODUCTION
import os
import sys
import pandas as pd
from src.main import main

# =============================================================================
# CONFIGURATION AWS - À ADAPTER AVEC VOS CREDENTIALS
# =============================================================================

# Option 1: Credentials hardcodés (DÉCONSEILLÉ en production)
# os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAIOSFODNN7EXAMPLE'
# os.environ['AWS_SECRET_ACCESS_KEY'] = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

# Option 2: Credentials via variables d'environnement (RECOMMANDÉ)
# Exporter dans le shell avant d'exécuter:
# export AWS_ACCESS_KEY_ID="your_access_key"
# export AWS_SECRET_ACCESS_KEY="your_secret_key"

# Option 3: Le script utilisera automatiquement:
# - ~/.aws/credentials si configuré avec 'aws configure'
# - Variables d'environnement AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY
# - IAM Role si exécuté sur EC2

def run_production_pipeline():
    """
    Exécute le pipeline SMS en mode production avec données S3 réelles
    """
    print("=" * 60)
    print("🚀 PIPELINE SMS - MODE PRODUCTION RÉELLE")
    print("=" * 60)
    
    print("📋 Configuration:")
    print(f"   • Source: AWS S3")
    print(f"   • Mode: Données réelles")
    print(f"   • Credentials: {'Configurés' if 'AWS_ACCESS_KEY_ID' in os.environ else 'À configurer'}")
    
    print("\n🔄 Démarrage du traitement...")
    
    try:
        # Exécution du pipeline principal
        result = main()
        
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS DE PRODUCTION")
        print("=" * 50)
        
        if not result.empty:
            # Analyse des résultats
            total = len(result)
            credits = result[result['message_type'] == 'CREDIT']
            debits = result[result['message_type'] == 'DEBIT']
            
            print(f"✅ SUCCÈS: {total} transactions extraites")
            print(f"📈 Statistiques:")
            print(f"   • Crédits: {len(credits)} transactions")
            print(f"   • Débits: {len(debits)} transactions") 
            print(f"   • Services: {result['service_name'].nunique()}")
            print(f"   • Montant total: {result['amount'].sum():,.2f} XOF")
            
            # Répartition par service
            print(f"\n🏦 Répartition par service:")
            for service, count in result['service_name'].value_counts().items():
                print(f"   • {service}: {count} transactions")
            
            # Sauvegarde des résultats
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            result.to_csv(f"production_results_{timestamp}.csv", index=False)
            result.to_csv("production_latest.csv", index=False)
            
            print(f"\n💾 Fichiers générés:")
            print(f"   • production_results_{timestamp}.csv")
            print(f"   • production_latest.csv")
            
            # Aperçu
            print(f"\n👀 Aperçu des transactions:")
            preview = result[['service_name', 'message_type', 'amount', 'label']].head()
            print(preview.to_string(index=False))
            
            return result
            
        else:
            print("❌ AUCUNE transaction extraite")
            print("💡 Vérifiez:")
            print("   - Les credentials AWS")
            print("   - L'existence du fichier S3")
            print("   - Le format des données SMS")
            return None
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("\n🔧 Diagnostic:")
        print("   1. Vérifiez vos credentials AWS")
        print("   2. Testez: aws s3 ls s3://votre-bucket/")
        print("   3. Vérifiez les logs détaillés")
        return None

def main():
    """
    Point d'entrée principal du script
    """
    return run_production_pipeline()

if __name__ == "__main__":
    result = main()
    
    # Code de retour pour les scripts shell
    if result is not None and not result.empty:
        sys.exit(0)  # Succès
    else:
        sys.exit(1)  # Échec