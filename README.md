# 🚀 Pipeline de Traitement SMS Bancaires

Système d'extraction et de structuration automatique de données financières depuis des SMS bancaires et mobiles money.

## 📋 Fonctionnalités

- ✅ **Extraction automatique** depuis AWS S3
- ✅ **Traitement multi-services** (Orange Money, MTN, Wave, Moov, etc.)
- ✅ **Classification intelligente** CREDIT/DEBIT
- ✅ **Extraction des données** : montants, dates, contreparties, soldes
- ✅ **Filtrage des SMS promotionnels**
- ✅ **Export CSV/DataFrame** prêt pour analyse
- ✅ **Statistiques détaillées** et logging complet

## 🛠️ Installation

```bash
# Cloner le repository
git clone https://github.com/FranckAmemou/sms-processing-pipeline.git
cd sms-processing-pipeline

# Installer les dépendances
pip install -r requirements.txt

# Configurer AWS (si pas déjà fait)
aws configure


## Votre README.md final :

```markdown
# 🚀 Pipeline de Traitement SMS Bancaires

## 📁 Structure du Projet

```plaintext
sms-processing-pipeline/
├── run_pipeline.py
├── requirements.txt
├── src/
│   ├── main.py
│   ├── classifiers/
│   │   ├── sms_classifier.py
│   │   ├── label_classifier.py
│   │   └── account_classifier.py
│   ├── config/
│   │   ├── settings.py
│   │   └── services.py
│   ├── core/
│   │   ├── s3_client.py
│   │   ├── text_normalizer.py
│   │   └── currency_converter.py
│   ├── extractors/
│   │   ├── amount_extractor.py
│   │   ├── date_extractor.py
│   │   ├── balance_extractor.py
│   │   ├── counterparty_extractor.py
│   │   ├── reference_extractor.py
│   │   ├── tax_extractor.py
│   │   └── currency_extractor.py
│   ├── processors/
│   │   ├── sms_processor.py
│   │   └── multi_operation_processor.py
│   └── utils/
│       ├── logger.py
│       ├── helpers.py
```
