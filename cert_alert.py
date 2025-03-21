import requests
import sqlite3
from bs4 import BeautifulSoup

CERT_URL = "https://www.cert.ssi.gouv.fr/"

response = requests.get(CERT_URL)
soup = BeautifulSoup(response.text, "html.parser")

date_alert = soup.find("span", class_="item-date")
alert_date = date_alert.text.strip() if date_alert else "Date inconnue"

title_div = soup.find("div", class_="item-title")
alert_link = title_div.find("a")  # Le lien <a> contient l'ID et le titre
alert_id = alert_link['href'].split('/')[-2] if alert_link else "ID non trouvé"
alert_title = alert_link.text.strip() if alert_link else "Titre non trouvé"

status_alert = soup.find("span", class_="item-status")
alert_status = status_alert.text.strip() if status_alert else "État non trouvé"

print(f"Date : {alert_date}")
print(f"ID de l'alerte : {alert_id}")
print(f"Titre de l'alerte : {alert_title}")
print(f"État de l'alerte : {alert_status}")

conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO cert_alerts (alert_date, alert_id, alert_text, alert_status)
VALUES (?, ?, ?, ?)
""", (alert_date, alert_id, alert_title, alert_status))

conn.commit()
conn.close()

print(f"Alerte CERT enregistrée : {alert_id} - {alert_title} - {alert_status}")
