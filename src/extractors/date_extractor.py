import re
from datetime import datetime

class DateExtractor:
    
    def extract_operation_date(self, normalized_body):
        """Extrait la date de l'opération du message SMS"""
        date_patterns = [
            r'DATE[:\s]*(\d{2}-\d{2}-\d{4})\s+\d{2}:\d{2}:\d{2}',
            r'(\d{2}-\d{2}-\d{4})\s+\d{2}:\d{2}:\d{2}',
            r'(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}:\d{2}',
            r'(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}',
            r'LE\s+(\d{4}-\d{2}-\d{2})(?=\s+\d{2}:\d{2}:\d{2}|\s+SOLDE|\s|$)',
            r'LE\s+(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}',
            r'(\d{4}-\d{2}-\d{2})(?=\s+\d{2}:\d{2}:\d{2}|\s+SOLDE|\s|$)',
            r'(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}',
            r'LE\s+(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{4})(?=\s+\d{2}:\d{2}:\d{2}|\s+SOLDE|\s|$)',
            # Patterns supplémentaires pour divers formats
            r'DU\s+(\d{2}/\d{2}/\d{4})',
            r'AU\s+(\d{2}/\d{2}/\d{4})',
            r'DATE\s+:\s+(\d{2}/\d{2}/\d{4})',
            r'DATE\s+:\s+(\d{2}-\d{2}-\d{4})',
            r'LE\s+(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})(?=\s+à\s+\d{1,2}:\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})(?=\s+-\s+\d{1,2}:\d{2})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, normalized_body)
            if match:
                date_str = match.group(1).strip()
                normalized_date = self.normalize_date(date_str)
                if normalized_date:
                    return normalized_date

        return None

    def normalize_date(self, date_str):
        """Normalise la date vers le format YYYY-MM-DD"""
        try:
            # Format déjà normalisé
            if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                return date_str
            
            # Format DD/MM/YYYY
            elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
                day, month, year = date_str.split('/')
                day = day.zfill(2)
                month = month.zfill(2)
                return f"{year}-{month}-{day}"
            
            # Format DD-MM-YYYY
            elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', date_str):
                day, month, year = date_str.split('-')
                day = day.zfill(2)
                month = month.zfill(2)
                return f"{year}-{month}-{day}"
            
            # Format YYYY/MM/DD
            elif re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
                year, month, day = date_str.split('/')
                month = month.zfill(2)
                day = day.zfill(2)
                return f"{year}-{month}-{day}"
                
        except Exception:
            pass

        return None

    def extract_date_from_multi_operation(self, operation_text):
        """Extrait la date spécifique pour les opérations multiples"""
        # Patterns pour les dates dans les mini-relevés
        date_patterns = [
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{2}-\d{2}-\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, operation_text)
            if match:
                date_str = match.group(1).strip()
                normalized_date = self.normalize_date(date_str)
                if normalized_date:
                    return normalized_date
        return None

    def is_valid_date(self, date_str):
        """Valide si une chaîne est une date valide"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False