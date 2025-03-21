import requests
import sqlite3
from bs4 import BeautifulSoup

# URL du CERT
CERT_URL = "https://www.cert.ssi.gouv.fr/"

# Récupérer le contenu de la page
response = requests.get(CERT_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Extraire la date de l'alerte
date_alert = soup.find("span", class_="item-date")  # La date est dans un <span class="item-date">
alert_date = date_alert.text.strip() if date_alert else "Date inconnue"

# Extraire l'ID et le titre de l'alerte
title_div = soup.find("div", class_="item-title")  # Le titre et l'ID sont dans un <div class="item-title">
alert_link = title_div.find("a")  # Le lien <a> contient l'ID et le titre
alert_id = alert_link['href'].split('/')[-2] if alert_link else "ID non trouvé"
alert_title = alert_link.text.strip() if alert_link else "Titre non trouvé"

# Extraire l'état de l'alerte
status_alert = soup.find("span", class_="item-status")  # L'état est dans un <span class="item-status">
alert_status = status_alert.text.strip() if status_alert else "État non trouvé"

# Afficher les alertes pour vérifier
print(f"Date : {alert_date}")
print(f"ID de l'alerte : {alert_id}")
print(f"Titre de l'alerte : {alert_title}")
print(f"État de l'alerte : {alert_status}")

# Connexion à la base de données SQLite
conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

# Insérer l'alerte dans la table cert_alerts
cursor.execute("""
INSERT INTO cert_alerts (alert_date, alert_id, alert_text, alert_status)
VALUES (?, ?, ?, ?)
""", (alert_date, alert_id, alert_title, alert_status))

# Commit et fermeture de la connexion à la base de données
conn.commit()
conn.close()

print(f"Alerte CERT enregistrée : {alert_id} - {alert_title} - {alert_status}")
