import json
import subprocess
import sqlite3
import re
import os
import shutil

# Fonction pour extraire un nombre avec une expression régulière
def extract_number(output, regex_pattern):
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

# Fonction pour effectuer la collecte des données et les insérer dans la base de données
def collect_data():
    base_path = "/home/cristiano/projet/ams"  # Ton chemin absolu

    with open(os.path.join(base_path, 'config.json'), 'r') as f:
        config = json.load(f)

    conn = sqlite3.connect(os.path.join(base_path, "monitoring.db"))
    cursor = conn.cursor()

    for sonde in config['sondes']:
        script_path = os.path.join(base_path, sonde['script'])

        if script_path.endswith('.py'):
            cmd = f"python3 {script_path}"
        elif script_path.endswith('.sh'):
            cmd = f"bash {script_path}"
        else:
            print(f"Format de script non pris en charge : {script_path}")
            continue

        output = subprocess.getoutput(cmd)

        if sonde['type'] == 'cpu':
            cpu_usage = extract_number(output, r'CPU : ([\d.]+)')
            cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('cpu', cpu_usage))
        elif sonde['type'] == 'disque':
            disk_usage = extract_number(output, r'Disque : ([\d.]+)')
            cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('disque', disk_usage))
        elif sonde['type'] == 'utilisateurs':
            users_connected = int(extract_number(output, r'User : (\d+)'))
            cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('utilisateurs', users_connected))

        print(f"Donnée insérée pour {sonde['type']}")

    conn.commit()
    conn.close()
    print("Toutes les données ont été insérées avec succès !")

# Fonction pour effectuer une sauvegarde de la base de données
def backup_database():
    base_path = "/home/cristiano/projet/ams"
    db_path = os.path.join(base_path, "monitoring.db")
    backup_path = os.path.join(base_path, "monitoring_backup.db")

    try:
        # Copie la base de données vers un fichier de sauvegarde
        shutil.copy2(db_path, backup_path)
        print(f"Base de données sauvegardée sous {backup_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la base de données: {e}")

# Fonction pour restaurer la base de données à partir d'une sauvegarde
def restore_database():
    base_path = "/home/cristiano/projet/ams"
    db_path = os.path.join(base_path, "monitoring.db")
    backup_path = os.path.join(base_path, "monitoring_backup.db")

    try:
        # Remplace la base de données actuelle par la sauvegarde
        shutil.copy2(backup_path, db_path)
        print(f"Base de données restaurée à partir de {backup_path}")
    except Exception as e:
        print(f"Erreur lors de la restauration de la base de données: {e}")

    collect_data()

