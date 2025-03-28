import pygal
import sqlite3
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# Définition des chemins
BASE_PATH = "/home/cristiano/projet/ams"
GRAPH_DIR = os.path.join(BASE_PATH, "graphs")
TEMPLATE_PATH = os.path.join(BASE_PATH, "mail_template.txt")
os.makedirs(GRAPH_DIR, exist_ok=True)

# Fonction pour générer un graphique pour une sonde donnée
def generate_graph(sonde_type):
    db_path = os.path.join(BASE_PATH, "monitoring.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp, value FROM system_data WHERE type=?", (sonde_type,))
    data = cursor.fetchall()

    # Formatage des données pour pygal
    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in data]
    values = [row[1] for row in data]

    # Création du graphique
    chart = pygal.Line()
    chart.title = f"Historique des valeurs pour la sonde {sonde_type}"
    chart.x_labels = [timestamp.strftime('%Y-%m-%d %H:%M:%S') for timestamp in timestamps]
    chart.add(sonde_type, values)

    chart_path = os.path.join(GRAPH_DIR, f"{sonde_type}_graph.svg")
    chart.render_to_file(chart_path)
    print(f"Graphique généré pour {sonde_type} : {chart_path}")

# Fonction pour envoyer un e-mail
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

# Fonction pour détecter une crise et envoyer une alerte
def detect_crisis(sonde_type, seuil=80):
    db_path = os.path.join(BASE_PATH, "monitoring.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp, value FROM system_data WHERE type=?", (sonde_type,))
    data = cursor.fetchall()

    # Vérification si une valeur dépasse le seuil de crise
    for row in data:
        if row[1] >= seuil:
            timestamp = row[0]
            message = f"Alerte : La sonde {sonde_type} a dépassé le seuil de crise ({seuil}%) à {timestamp} avec une valeur de {row[1]}%"
            send_email(message)
            break

# Exemple d'utilisation
if __name__ == "__main__":
    generate_graph("cpu")  # Remplacer "cpu" par le type de sonde souhaité
    detect_crisis("cpu", 85)  # Vérifier une crise pour la sonde CPU avec un seuil de 85%
