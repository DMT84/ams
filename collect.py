import json
import subprocess
import sqlite3
import re
import os
import time
import argparse
import tarfile

# Définition des chemins
BASE_PATH = "/home/cristiano/projet/ams"  # Ton chemin absolu
DB_PATH = os.path.join(BASE_PATH, "monitoring.db")
DATA_DIR = os.path.join(BASE_PATH, "data")
BACKUP_DIR = os.path.join(BASE_PATH, "backups")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Fonction pour extraire le nombre de la sortie du script
def extract_number(output, regex_pattern):
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

# Fonction pour créer une sauvegarde
def backup():
    backup_name = os.path.join(BACKUP_DIR, f"backup_{int(time.time())}.tar.gz")
    with tarfile.open(backup_name, "w:gz") as tar:
        tar.add(DB_PATH, arcname="monitoring.db")
        tar.add(DATA_DIR, arcname="data")
    print(f"Sauvegarde créée : {backup_name}")

# Fonction pour restaurer une sauvegarde
def restore(archive_path):
    if os.path.exists(archive_path):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(BASE_PATH)
        print(f"Sauvegarde restaurée depuis : {archive_path}")
    else:
        print(f"Fichier {archive_path} introuvable")

# Fonction principale pour collecter des données et les insérer dans la base
def collect_data():
    with open(os.path.join(BASE_PATH, 'config.json'), 'r') as f:
        config = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for sonde in config['sondes']:
        script_path = os.path.join(BASE_PATH, sonde['script'])

        if script_path.endswith('.py'):
            cmd = f"python3 {script_path}"
        elif script_path.endswith('.sh'):
            cmd = f"bash {script_path}"
        else:
            print(f"❌ Format de script non pris en charge : {script_path}")
            continue

        output = subprocess.getoutput(cmd)

        # Traitement des données
        if sonde['type'] == 'cpu':
            cpu_usage = extract_number(output, r'CPU : ([\d.]+)')
            cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('cpu', cpu_usage))
        elif sonde['type'] == 'disque':
            disk_usage = extract_number(output, r'Disque : ([\d.]+)')
            cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('disque', disk_usage))
        elif sonde['type'] == 'utilisateurs':
            users_connected = int(extract_number(output, r'User : (\d+)'))
            cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('utilisateurs', users_connected))

        print(f"✅ Donnée insérée pour {sonde['type']}")

    conn.commit()
    conn.close()
    print("📥 Toutes les données ont été insérées avec succès !")

# Lancement de la collecte
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collecte de données et gestion des sauvegardes")
    parser.add_argument('--backup', action='store_true', help="Effectuer une sauvegarde")
    parser.add_argument('--restore', type=str, help="Restaurer une sauvegarde")
    args = parser.parse_args()

    if args.backup:
        backup()
    elif args.restore:
        restore(args.restore)
    else:
        collect_data()
