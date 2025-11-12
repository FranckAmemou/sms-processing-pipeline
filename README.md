# SMS Transaction Processor

Pipeline de traitement intelligent des SMS bancaires et financiers pour l'extraction de transactions.

## Fonctionnalités

- Extraction des montants, soldes, taxes et références
- Classification automatique des types de transactions
- Support multi-devises (XOF, USD, EUR)
- Traitement des SMS multi-opérations
- Intégration S3 et BigQuery
---------------------------------------
guide
sms-processing-pipeline/
├── 📄 run_pipeline.py              # Script principal d'exécution
├── 📄 requirements.txt             # Dépendances Python
├── 📁 src/                         # Code source principal
│   ├── 📄 main.py                 # Point d'entrée principal
│   ├── 📁 classifiers/            # Classification des SMS
│   │   ├── 📄 sms_classifier.py   # Classification CREDIT/DEBIT
│   │   ├── 📄 label_classifier.py # Étiquetage des transactions
│   │   └── 📄 account_classifier.py # Classification des comptes
│   ├── 📁 config/                 # Configuration
│   │   ├── 📄 settings.py         # Paramètres S3 et AWS
│   │   └── 📄 services.py         # Services autorisés
│   ├── 📁 core/                   # Composants fondamentaux
│   │   ├── 📄 s3_client.py        # Client AWS S3
│   │   ├── 📄 text_normalizer.py  # Normalisation de texte
│   │   └── 📄 currency_converter.py # Conversion de devises
│   ├── 📁 extractors/             # Extracteurs de données
│   │   ├── 📄 amount_extractor.py # Extraction des montants
│   │   ├── 📄 date_extractor.py   # Extraction des dates
│   │   ├── 📄 balance_extractor.py # Extraction des soldes
│   │   ├── 📄 counterparty_extractor.py # Extraction contreparties
│   │   ├── 📄 reference_extractor.py # Extraction références
│   │   ├── 📄 tax_extractor.py    # Extraction des taxes
│   │   └── 📄 currency_extractor.py # Extraction des devises
│   ├── 📁 processors/             # Traitement des SMS
│   │   ├── 📄 sms_processor.py    # Processeur principal SMS
│   │   └── 📄 multi_operation_processor.py # Processeur multi-opérations
│   └── 📁 utils/                  # Utilitaires
│       ├── 📄 logger.py           # Configuration logging
│       ├── 📄 helpers.py          # Fonctions helper

## Installation

```bash
pip install -r requirements.txt
