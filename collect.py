import json
import subprocess
import sqlite3
import re
import os
import shutil  
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        valeur = extract_number(output, r'([\d.]+)')
        cursor.execute("INSERT INTO system_data (type, value) VALUES (?, ?)", (sonde['type'], valeur))
        print(f"Donnée insérée pour {sonde['type']} : {valeur}")
    
    conn.commit()
    conn.close()
    print("Toutes les données ont été insérées avec succès !")

collect_data()

def backup_database():
    base_path = "/home/cristiano/projet/ams"  
    db_path = os.path.join(base_path, "monitoring.db")
    backup_path = os.path.join(base_path, "monitoring_backup.db")

    try:
        shutil.copy2(db_path, backup_path)
        print(f"Base de données sauvegardée sous {backup_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la base de données: {e}")

def restore_database():
    base_path = "/home/cristiano/projet/ams" 
    db_path = os.path.join(base_path, "monitoring.db")
    backup_path = os.path.join(base_path, "monitoring_backup.db")

    try:
        shutil.copy2(backup_path, db_path)
        print(f"Base de données restaurée à partir de {backup_path}")
    except Exception as e:
        print(f"Erreur lors de la restauration de la base de données: {e}")

def envoyer_alerte(sujet, message):
    sender_email = "dimitri.botella@alumni.univ-avignon.fr"
    receiver_email = "dimitri.botella@alumni.univ-avignon.fr"
    smtp_server = "partage.univ-avignon.fr"
    smtp_port = 465
    username = sender_email
    password = os.getenv("SMTP_PASSWORD")  # Stocke le mot de passe en variable d'environnement

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
        print("Alerte envoyée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'alerte : {e}")

def verifier_alertes():
    base_path = "/home/cristiano/projet/ams"
    db_path = os.path.join(base_path, "monitoring.db")
    
    conn = sqlite3.connect(db_path)
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
            print(f"Alerte envoyée pour {sonde} à {result[0]}%")

    conn.close()

if __name__ == "__main__":
    verifier_alertes()
