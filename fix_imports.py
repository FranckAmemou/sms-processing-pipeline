# fix_imports.py
import os
import re

def fix_imports_in_file(filepath):
    """Corrige les imports relatifs dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les imports relatifs
        new_content = re.sub(r'from \.\.(\w+)', r'from \1', content)
        new_content = re.sub(r'from \.(\w+)', r'from \1', new_content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Corrigé: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ Erreur avec {filepath}: {e}")
        return False

print("🔧 Correction des imports relatifs...")

# Compter les corrections
fixed_count = 0

# Corriger tous les fichiers dans src/
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            if fix_imports_in_file(filepath):
                fixed_count += 1

print(f"🎉 {fixed_count} fichiers corrigés !")

# Vérification finale
print("\n🔍 Vérification des imports relatifs restants...")
import subprocess
result = subprocess.run(['grep', '-r', 'from \\.', 'src/'], capture_output=True, text=True)
if result.stdout:
    print("❌ Imports relatifs trouvés:")
    print(result.stdout)
else:
    print("✅ Aucun import relatif trouvé")
