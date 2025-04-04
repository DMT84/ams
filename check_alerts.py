import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

BASE_PATH = "/home/cristiano/projet/ams"
DB_PATH = os.path.join(BASE_PATH, "monitoring.db")
TEMPLATE_PATH = os.path.join(BASE_PATH, "email_template.txt")

def envoyer_alerte(sujet, sonde, valeur, seuil):
    sender_email = "dimitri.botella@alumni.univ-avignon.fr"
    receiver_email = "dimitri.botella@alumni.univ-avignon.fr"
    smtp_server = "partage.univ-avignon.fr"
    smtp_port = 465
    username = sender_email
    password = os.getenv("SMTP_PASSWORD")

    # Lire le template d'e-mail
    try:
        with open(TEMPLATE_PATH, 'r') as f:
            template = f.read()
        message = template.format(sonde=sonde, valeur=valeur, seuil=seuil)
    except Exception as e:
        print(f"Erreur lecture template : {e}")
        message = f"Alerte sur la sonde {sonde} : {valeur}% (seuil : {seuil}%)"

    # Préparer et envoyer l'e-mail
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
        print(f"Erreur alerte email: {e}")

def verifier_alertes():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        alertes = {
            "cpu": (90, "Alerte CPU"),
            "disque": (95, "Alerte Disque Plein")
        }

        for sonde, (seuil, sujet) in alertes.items():
            cursor.execute("SELECT value FROM system_data WHERE type=? ORDER BY rowid DESC LIMIT 1", (sonde,))
            result = cursor.fetchone()

            if result and result[0] >= seuil:
                envoyer_alerte(sujet, sonde, result[0], seuil)
                print(f"Alerte envoyée pour {sonde} à {result[0]}%")

        conn.close()
    except Exception as e:
        print(f"Erreur vérification alertes : {e}")

if __name__ == "__main__":
    verifier_alertes()
