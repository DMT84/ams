import json
import subprocess
import sqlite3
import re

def extract_number(output, regex_pattern):
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

with open('config.json', 'r') as f:
    config = json.load(f)

conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

for sonde in config['sondes']:
    # Exécuter le script associé à la sonde
    output = subprocess.getoutput(f"python3 {sonde['script']}" if sonde['script'].endswith('.py') else sonde['script'])
    
    # Traiter la sortie en fonction du type de sonde
    if sonde['type'] == 'cpu':
        cpu_usage = extract_number(output, r'CPU : ([\d.]+)')
        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('cpu', cpu_usage))
    elif sonde['type'] == 'disque':
        disk_usage = extract_number(output, r'Disque : ([\d.]+)')
        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('disque', disk_usage))
    elif sonde['type'] == 'utilisateurs':
        users_connected = int(extract_number(output, r'User : (\d+)'))
        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", ('utilisateurs', users_connected))

conn.commit()
conn.close()

print("Données insérées avec succès !")
