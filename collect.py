import json
import subprocess
import sqlite3
import re
import os
import shutil

BASE_PATH = "/home/cristiano/projet/ams"
DB_PATH = os.path.join(BASE_PATH, "monitoring.db")
BACKUP_PATH = os.path.join(BASE_PATH, "monitoring_backup.db")
CONFIG_PATH = os.path.join(BASE_PATH, "config.json")

def extract_number(output, regex_pattern):
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

def collect_data():
    with open(CONFIG_PATH, 'r') as f:
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
            print(f"Format non supporté : {script_path}")
            continue

        output = subprocess.getoutput(cmd)
        valeur = extract_number(output, r'([\d.]+)')
        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", (sonde['type'], valeur))
        print(f"Donnée insérée pour {sonde['type']} : {valeur}")

    conn.commit()
    conn.close()
    print("Collecte terminée.")
    
def run_backup():
    try:
        subprocess.run(["python3", os.path.join(BASE_PATH, "backup.py")])  # Appel du script backup.py
        print("Sauvegarde terminée.")
    except Exception as e:
        print(f"Erreur lancement backup.py : {e}")

def run_restore():
    try:
        subprocess.run(["python3", os.path.join(BASE_PATH, "restore.py")])  # Appel du script restore.py
        print("Restauration terminée.")
    except Exception as e:
        print(f"Erreur lancement restore.py : {e}")
def run_alert_check():
    try:
        subprocess.run(["python3", os.path.join(BASE_PATH, "check_alerts.py")])
        print("Vérification des alertes terminée.")
    except Exception as e:
        print(f"Erreur lancement check_alerts.py : {e}")

if __name__ == "__main__":
    collect_data()
    run_restore()
    run_backup()
    run_alert_check()
