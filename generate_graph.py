import sqlite3
import pygal
import os

DB_PATH = "monitoring.db"

def generate_graph(sonde_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, value FROM system_data WHERE type=? ORDER BY timestamp", (sonde_type,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        print(f"Aucune donnée pour {sonde_type}")
        return

    timestamps = [row[0] for row in data]
    values = [row[1] for row in data]

    chart = pygal.Line(title=f"Historique {sonde_type}", x_label_rotation=20)
    chart.x_labels = timestamps
    chart.add(sonde_type, values)
    chart.render_to_file(f"{sonde_type}_history.svg")
    print(f"Graphique généré : {sonde_type}_history.svg")

if __name__ == "__main__":
    for sonde in ["cpu", "disque", "utilisateurs"]:
        generate_graph(sonde)
