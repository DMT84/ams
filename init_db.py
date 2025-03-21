import sqlite3

conn = sqlite3.connect("monitoring.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS system_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type TEXT,
    value REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cert_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_text TEXT
)
""")

conn.commit()
conn.close()

print("✅ Base de données initialisée avec succès !")
