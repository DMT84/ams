import sqlite3

conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM system_data WHERE timestamp < datetime('now', '-7 days')")
cursor.execute("DELETE FROM cert_alerts WHERE timestamp < datetime('now', '-7 days')")

conn.commit()
conn.close()

print("Base nettoyée : données de plus de 7 jours supprimées.")

