import json
import subprocess
import sqlite3
import re
import os

def extract_number(output, regex_pattern):
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

def collect_data():
    base_path = "/home/cristiano/projet/ams"  

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

        # Traitement
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

collect_data()
