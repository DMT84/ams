import sqlite3
import subprocess
import re

def extract_number(output, regex_pattern):
    """Utilise une regex pour extraire un nombre depuis une sortie de commande"""
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

cpu_output = subprocess.getoutput("python3 sonde_cpu.py")
disk_output = subprocess.getoutput("python3 sonde_disque.py")
users_output = subprocess.getoutput("./sonde_user.sh")

cpu_usage = extract_number(cpu_output, r'CPU : ([\d.]+)')
disk_usage = extract_number(disk_output, r'Disque : ([\d.]+)')
users_connected = int(extract_number(users_output, r'User : (\d+)'))

conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

# Insertion des données pour chaque sonde avec un type spécifique
cursor.execute("""
INSERT INTO system_data (type, value)
VALUES (?, ?)
""", ("CPU", cpu_usage))

cursor.execute("""
INSERT INTO system_data (type, value)
VALUES (?, ?)
""", ("Disk", disk_usage))

cursor.execute("""
INSERT INTO system_data (type, value)
VALUES (?, ?)
""", ("Users", users_connected))

conn.commit()
conn.close()

print(f"Données insérées : CPU {cpu_usage}%, Disque {disk_usage}%, Utilisateurs {users_connected}")
