import json
import subprocess
import sqlite3
import re
import os
import smtplib
from email.mime.text import MIMEText
import pyrrd.rrd as rrd
import time
import argparse
import tarfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "monitoring.db")
TEMPLATE_PATH = os.path.join(BASE_DIR, "mail_template.txt")
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

def extract_number(output):
    match = re.search(r'([\d.]+)', output)
    return float(match.group(1)) if match else 0

def load_config():
    with open(os.path.join(BASE_DIR, "config.json")) as f:
        return json.load(f)

def send_email(message):
    with open(TEMPLATE_PATH) as f:
        template = f.read()
    content = template.replace("{{message}}", message)

    msg = MIMEText(content)
    msg['Subject'] = "Alerte : Situation de crise détectée"
    msg['From'] = "supervision@univ.fr"
    msg['To'] = "admin@univ.fr"

    try:
        with smtplib.SMTP('smtp.univ.fr', 25) as server:
            server.send_message(msg)
        print("Mail envoyé.")
    except Exception as e:
        print(f"Erreur envoi mail : {e}")

def init_rrd(sonde_type):
    path = os.path.join(DATA_DIR, f"{sonde_type}.rrd")
    if not os.path.exists(path):
        rrdtool = rrd.RRD(
            filename=path,
            step=60,
            ds=[rrd.DataSource(dsName='value', dsType='GAUGE', heartbeat=120)],
            rra=[rrd.RRA(cf='AVERAGE', xff=0.5, steps=1, rows=1440)]
        )
        rrdtool.create(debug=False)

def update_rrd(sonde_type, value):
    path = os.path.join(DATA_DIR, f"{sonde_type}.rrd")
    if os.path.exists(path):
        rrdtool = rrd.RRD(filename=path)
        rrdtool.bufferValue(str(int(time.time())), str(value))
        rrdtool.update(debug=False)

def backup():
    backup_name = os.path.join(BACKUP_DIR, f"backup_{int(time.time())}.tar.gz")
    with tarfile.open(backup_name, "w:gz") as tar:
        tar.add(DB_PATH, arcname="monitoring.db")
        tar.add(DATA_DIR, arcname="data")
    print(f"Sauvegarde créée : {backup_name}")

def restore(archive_path):
    if os.path.exists(archive_path):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(BASE_DIR)
        print(f"Sauvegarde restaurée depuis : {archive_path}")
    else:
        print(f"Fichier {archive_path} introuvable")

def collect_data():
    config = load_config()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS system_data 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      type TEXT, value REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    for sonde in config["sondes"]:
        print(f"Lecture {sonde['type']}...")
        output = subprocess.getoutput(
            f"python3 {sonde['script']}" if sonde['script'].endswith('.py') else f"bash {sonde['script']}"
        )
        value = extract_number(output)

        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", (sonde['type'], value))
        conn.commit()
        
        init_rrd(sonde['type'])
        update_rrd(sonde['type'], value)

        seuil = sonde.get("seuil", 100)
        if value >= seuil:
            msg = f"Sonde {sonde['type']} - Valeur critique détectée : {value}% (seuil : {seuil}%)"
            print(msg)
            send_email(msg)

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collecte & sauvegarde AMS")
    parser.add_argument('--backup', action='store_true', help="Effectuer une sauvegarde")
    parser.add_argument('--restore', type=str, help="Restaurer une sauvegarde")
    args = parser.parse_args()

    if args.backup:
        backup()
    elif args.restore:
        restore(args.restore)
    else:
        collect_data()
