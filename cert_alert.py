import requests
import sqlite3
from bs4 import BeautifulSoup

CERT_URL = "https://www.cert.ssi.gouv.fr/"

response = requests.get(CERT_URL)
soup = BeautifulSoup(response.text, "html.parser")

alert = soup.find("h2")
alert_text = alert.text.strip() if alert else "Pas d'alerte trouvée"

conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

cursor.execute("INSERT INTO cert_alerts (alert_text) VALUES (?)", (alert_text,))

conn.commit()
conn.close()

print(f"✅ Dernière alerte CERT enregistrée : {alert_text}")

