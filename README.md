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


## 📁 Structure du Projet avec Explications

```plaintext
sms-processing-pipeline/
├── run_pipeline.py              #  Script principal pour lancer le pipeline
├── requirements.txt             #  Liste des dépendances Python nécessaires
├── src/                         # Code source principal du projet
│   ├── main.py                  #  Point d'entrée principal, orchestre le traitement
│   ├── classifiers/             #  Modules de classification des SMS
│   │   ├── sms_classifier.py    #  Classifie CREDIT vs DEBIT selon le contenu
│   │   ├── label_classifier.py  #  Attribue des étiquettes aux transactions
│   │   └── account_classifier.py #  Identifie le type de compte concerné
│   ├── config/                  # Fichiers de configuration
│   │   ├── settings.py          # Paramètres AWS S3 et configuration globale
│   │   └── services.py          #  Liste des services financiers autorisés
│   ├── core/                    #  Composants fondamentaux
│   │   ├── s3_client.py         #  Client pour lire les données depuis AWS S3
│   │   ├── text_normalizer.py   #  Nettoie et normalise le texte des SMS
│   │   └── currency_converter.py #  Convertit entre XOF, USD, EUR
│   ├── extractors/              #  Modules d'extraction de données
│   │   ├── amount_extractor.py  #  Extrait les montants des transactions
│   │   ├── date_extractor.py    #  Extrait les dates d'opération
│   │   ├── balance_extractor.py #  Extrait les soldes après transaction
│   │   ├── counterparty_extractor.py #  Identifie la contrepartie (nom/téléphone)
│   │   ├── reference_extractor.py #  Extrait les références de transaction
│   │   ├── tax_extractor.py     #  Extrait les montants de frais et taxes
│   │   └── currency_extractor.py #  Identifie la devise de la transaction
│   ├── processors/              #  Modules de traitement métier
│   │   ├── sms_processor.py     #  Processeur principal pour un seul SMS
│   │   └── multi_operation_processor.py #  Gère les mini-relevés multi-opérations
│   └── utils/                   #  Utilitaires et helpers
│       ├── logger.py            #  Configuration centralisée du logging
│       ├── helpers.py           #  Fonctions utilitaires réutilisables
│       └── constants.py         #  Constantes et configurations globales
├── tests/                       #  Tests automatisés
│   ├── test_processors.py       #  Tests des processeurs de SMS
│   ├── test_extractors.py       #  Tests des extracteurs de données
│   ├── test_classifiers.py      #  Tests des classificateurs
│   └── test_integration.py      #  Tests d'intégration complets
```
