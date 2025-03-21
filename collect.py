import sqlite3
import subprocess
import re

def extract_number(output, regex_pattern):
    """Utilise une regex pour extraire un nombre depuis une sortie de commande"""
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

# Exécuter les sondes et récupérer les sorties
cpu_output = subprocess.getoutput("python3 sonde_cpu.py")
disk_output = subprocess.getoutput("python3 sonde_disque.py")
users_output = subprocess.getoutput("./sonde_users.sh")

# Appliquer la regex pour récupérer les valeurs
cpu_usage = extract_number(cpu_output, r'CPU : ([\d.]+)')
disk_usage = extract_number(disk_output, r'Disque : ([\d.]+)')
users_connected = int(extract_number(users_output, r'User : (\d+)'))  # Conversion en entier

# Connexion à SQLite
conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

# Insérer les données dans la base
cursor.execute("""
INSERT INTO system_data (cpu_usage, disk_usage, users_connected)
VALUES (?, ?, ?)
""", (cpu_usage, disk_usage, users_connected))

conn.commit()
conn.close()

print(f"✅ Données insérées : CPU {cpu_usage}%, Disque {disk_usage}%, Utilisateurs {users_connected}")
