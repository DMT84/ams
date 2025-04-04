import json
import subprocess
import sqlite3
import re
import os
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === Config globale ===
BASE_PATH = "/home/cristiano/projet/ams"
DB_PATH = os.path.join(BASE_PATH, "monitoring.db")
BACKUP_PATH = os.path.join(BASE_PATH, "monitoring_backup.db")
CONFIG_PATH = os.path.join(BASE_PATH, "config.json")

# === Utilitaires ===
def extract_number(output, regex_pattern):
    match = re.search(regex_pattern, output)
    return float(match.group(1)) if match else 0

def backup_database():
    try:
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Base de données sauvegardée sous {BACKUP_PATH}")
    except Exception as e:
        print(f"❌ Erreur sauvegarde DB: {e}")

def restore_database():
    if os.path.exists(BACKUP_PATH):
        try:
            shutil.copy2(BACKUP_PATH, DB_PATH)
            print(f"♻️  Base restaurée depuis {BACKUP_PATH}")
        except Exception as e:
            print(f"❌ Erreur restauration DB: {e}")
    else:
        print("⚠️  Aucun backup trouvé pour restaurer.")

def envoyer_alerte(sujet, message):
    sender_email = "dimitri.botella@alumni.univ-avignon.fr"
    receiver_email = "dimitri.botella@alumni.univ-avignon.fr"
    smtp_server = "partage.univ-avignon.fr"
    smtp_port = 465
    username = sender_email
    password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = sujet
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(username, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("📧 Alerte envoyée avec succès.")
    except Exception as e:
        print(f"❌ Erreur alerte email: {e}")

def verifier_alertes():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        alertes = {
            "cpu": (90, "Alerte CPU", "Le CPU est utilisé à {valeur}%"),
            "disque": (95, "Alerte Disque Plein", "Le disque est utilisé à {valeur}%")
        }

        for sonde, (seuil, sujet, message) in alertes.items():
            cursor.execute("SELECT value FROM system_data WHERE type=? ORDER BY rowid DESC LIMIT 1", (sonde,))
            result = cursor.fetchone()

            if result and result[0] >= seuil:
                envoyer_alerte(sujet, message.format(valeur=result[0]))
                print(f"🚨 Alerte envoyée pour {sonde} à {result[0]}%")

        conn.close()
    except Exception as e:
        print(f"❌ Erreur vérification alertes : {e}")

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
            print(f"⚠️ Format non supporté : {script_path}")
            continue

        output = subprocess.getoutput(cmd)
        valeur = extract_number(output, r'([\d.]+)')
        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", (sonde['type'], valeur))
        print(f"📥 Donnée insérée pour {sonde['type']} : {valeur}")

    conn.commit()
    conn.close()
    print("✅ Collecte terminée.")

# === Lancement intelligent ===
def database_ready():
    try:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError("DB manquante.")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1 FROM system_data LIMIT 1")
        conn.close()
        return True
    except Exception:
        return False

if __name__ == "__main__":
    if not database_ready():
        print("🛠 Base non fonctionnelle. Restauration en cours...")
        restore_database()

    collect_data()
    verifier_alertes()
    backup_database()
