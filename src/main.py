# src/main.py (VERSION CORRIGÉE)
import pandas as pd
from datetime import datetime
import logging

# Import des modules modulaires
from config.settings import S3_BUCKET, S3_KEY
from config.services import SERVICE_NAME_USED, IGNORE_KEYWORDS
from core.s3_client import load_csv_from_s3
from processors.sms_processor import SMSProcessor
from utils.logger import setup_logger

logger = setup_logger()

class SMSProcessingPipeline:
    def __init__(self):
        self.stats = {
            'total_sms': 0,
            'processed': 0,
            'ignored': 0,
            'ignored_by_service': 0,
            'ignored_by_keywords': 0,
            'transactions_generated': 0
        }
        self.sms_processor = SMSProcessor()
    
    def extract_transactions(self, s3_bucket=None, s3_key=None, **kwargs):
        """Fonction principale pour extraire les transactions depuis S3"""
        logger.info("=== DÉMARRAGE DU TRAITEMENT SMS ===")
        
        # Chargement des données
        df = self._load_data(s3_bucket, s3_key, kwargs)
        if df is None:
            return pd.DataFrame()
            
        # Analyse initiale des services
        self._analyze_services(df)
            
        # Traitement
        processed_data = self._process_sms_batch(df, s3_key)
        
        # Création du DataFrame final
        result_df = self._create_final_dataframe(processed_data, s3_bucket, s3_key)
        
        # Statistiques
        self._log_statistics(result_df)
        
        return result_df
    
    def _load_data(self, s3_bucket, s3_key, kwargs):
        """Charge les données depuis S3"""
        df = load_csv_from_s3(s3_bucket, s3_key, 
                            kwargs.get('aws_access_key_id'), 
                            kwargs.get('aws_secret_access_key'))
        
        if df is None or df.empty:
            logger.error("Aucune donnée chargée depuis S3")
            return None
            
        logger.info(f"Données chargées: {len(df)} SMS")
        self.stats['total_sms'] = len(df)
        return df
    
    def _analyze_services(self, df):
        """Analyse la distribution des services SMS"""
        service_stats = {}
        
        for _, row in df.iterrows():
            sender = str(row.get('Sender ID', ''))
            if sender not in service_stats:
                service_stats[sender] = 0
            service_stats[sender] += 1
        
        logger.info(f"Services distincts trouvés: {len(service_stats)}")
        logger.info(f"Services autorisés configurés: {len(SERVICE_NAME_USED)}")
        
        # Afficher les services les plus fréquents
        logger.info("Top 10 des services les plus fréquents:")
        for service, count in sorted(service_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            status = "AUTORISÉ" if service in SERVICE_NAME_USED else "IGNORÉ"
            logger.info(f"  {service}: {count} SMS ({status})")
    
    def _process_sms_batch(self, df, s3_key):
        """Traite un batch de SMS"""
        processed_data = []
        
        for _, row in df.iterrows():
            try:
                sender = str(row.get('Sender ID', ''))
                
                if self.sms_processor.should_ignore(row):
                    self.stats['ignored'] += 1
                    # Déterminer pourquoi le SMS est ignoré
                    if sender not in SERVICE_NAME_USED:
                        self.stats['ignored_by_service'] += 1
                    else:
                        self.stats['ignored_by_keywords'] += 1
                    continue
                
                result = self.sms_processor.process_sms(row, s3_key)
                if result:
                    processed_data.extend(result)
                    self.stats['processed'] += 1
                else:
                    # Cas où le SMS est autorisé mais ne produit pas de transaction
                    self.stats['ignored'] += 1
                    self.stats['ignored_by_keywords'] += 1
                    
            except Exception as e:
                logger.error(f"Erreur traitement SMS: {e}")
                continue
                
        self.stats['transactions_generated'] = len(processed_data)
        return processed_data
    
    def _create_final_dataframe(self, processed_data, s3_bucket, s3_key):
        """Crée le DataFrame final avec formatage BigQuery"""
        if not processed_data:
            return pd.DataFrame()
            
        result_df = pd.DataFrame(processed_data)
        result_df['data_source'] = f"s3://{s3_bucket}/{s3_key}"
        
        # Formatage pour BigQuery
        result_df = self._format_for_bigquery(result_df)
        
        return result_df
    
    def _format_for_bigquery(self, df):
        """Formate les colonnes pour BigQuery - CORRIGÉ POUR LES DATES DD/MM"""
        try:
            # Convertir event_time en datetime
            if 'event_time' in df.columns:
                df['event_time'] = pd.to_datetime(df['event_time'], errors='coerce')
            
            # CORRECTION : Gestion du format de date DD/MM
            if 'operation_date' in df.columns:
                # Essayer de parser avec le format jour/mois
                df['operation_date'] = pd.to_datetime(
                    df['operation_date'], 
                    format='%d/%m',  # Format jour/mois
                    errors='coerce'
                )
                
                # Si parsing échoue, essayer d'autres formats
                if df['operation_date'].isna().any():
                    logger.warning("Certaines dates n'ont pas pu être parsées avec format DD/MM, tentative avec parsing automatique")
                    df['operation_date'] = pd.to_datetime(
                        df['operation_date'], 
                        errors='coerce'
                    )
                
                # Convertir en date (sans l'année)
                df['operation_date'] = df['operation_date'].dt.date
                
                # Vérifier s'il reste des dates invalides
                invalid_dates = df['operation_date'].isna()
                if invalid_dates.any():
                    logger.warning(f"Remplacement de {invalid_dates.sum()} dates invalides par la date actuelle")
                    df.loc[invalid_dates, 'operation_date'] = datetime.now().date()
            
            # Gérer processed_at
            if 'processed_at' in df.columns:
                df['processed_at'] = pd.to_datetime(df['processed_at'], errors='coerce')
            else:
                df['processed_at'] = pd.Timestamp.now()
                
        except Exception as e:
            logger.error(f"Erreur lors du formatage BigQuery: {e}")
            # Continuer sans formatage des dates plutôt que de planter
            
        return df
    
    def _log_statistics(self, result_df):
        """Log les statistiques de traitement détaillées"""
        logger.info("=== STATISTIQUES FINALES ===")
        logger.info(f"📨 SMS analysés: {self.stats['total_sms']}")
        logger.info(f"✅ SMS traités avec succès: {self.stats['processed']}")
        logger.info(f"⏭️ SMS ignorés: {self.stats['ignored']}")
        logger.info(f"  └ Ignorés par service non autorisé: {self.stats['ignored_by_service']}")
        logger.info(f"  └ Ignorés par mots-clés: {self.stats['ignored_by_keywords']}")
        logger.info(f"💳 Transactions générées: {self.stats['transactions_generated']}")
        
        if self.stats['total_sms'] > 0:
            taux_traitement = self.stats['processed'] / self.stats['total_sms'] * 100
            logger.info(f"📈 Taux de traitement: {taux_traitement:.1f}%")
            
            if taux_traitement < 10:
                logger.warning("ATTENTION: Taux de traitement très bas! Vérifiez SERVICE_NAME_USED")
        
        if not result_df.empty:
            logger.info("🎯 Répartition par type de message:")
            for msg_type, count in result_df['message_type'].value_counts().items():
                logger.info(f"  └ {msg_type}: {count}")
            
            logger.info("🏦 Répartition par service:")
            for service, count in result_df['service_name'].value_counts().items():
                logger.info(f"  └ {service}: {count}")
                
            if 'amount' in result_df.columns:
                credits = result_df[result_df['message_type'] == 'CREDIT']['amount'].sum()
                debits = result_df[result_df['message_type'] == 'DEBIT']['amount'].sum()
                logger.info(f"💰 Total crédits: {credits:,.2f} XOF")
                logger.info(f"💰 Total débits: {debits:,.2f} XOF")
                logger.info(f"💰 Solde net: {(credits - debits):,.2f} XOF")

def main():
    """Fonction principale pour exécution en standalone"""
    logger.info("=== DÉMARRAGE DU PIPELINE DE TRAITEMENT SMS ===")
    
    # Validation de la configuration
    logger.info("=== CONFIGURATION ===")
    logger.info(f"Services autorisés configurés: {len(SERVICE_NAME_USED)}")
    logger.info(f"Mots-clés d'ignore: {len(IGNORE_KEYWORDS)}")
    
    pipeline = SMSProcessingPipeline()
    
    result = pipeline.extract_transactions(
        s3_bucket=S3_BUCKET,
        s3_key=S3_KEY
    )
    
    if not result.empty:
        logger.info(f"✅ SUCCÈS: {len(result)} transactions extraites")
        logger.info("Aperçu des résultats:")
        logger.info(result[['service_name', 'message_type', 'amount', 'label']].head(10).to_string())
    else:
        logger.error("❌ AUCUNE transaction extraite")
    
    return result

if __name__ == "__main__":
    main()