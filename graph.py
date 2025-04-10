import sqlite3
import pygal
import os
from pathlib import Path

conn = sqlite3.connect("/home/cristiano/projet/ams/monitoring.db")
cursor = conn.cursor()

output_dir = Path("/home/cristiano/projet/ams/graphs")
output_dir.mkdir(parents=True, exist_ok=True)

html_output = output_dir / "graphiques_sondes.html"
with open(html_output, 'w') as f:
    f.write("""
    <html>
    <head>
        <title>Graphiques des sondes</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1, h2 {
                color: #333;
            }
            object {
                display: block;
                margin: 20px auto;
            }
            table {
                margin: 0 auto 50px;
                border-collapse: collapse;
                width: 80%;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            th, td {
                border: 1px solid #ccc;
                padding: 10px;
            }
            th {
                background-color: #eee;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
    <h1>Graphiques des sondes</h1>
    """)

    sondes = ["cpu", "disque", "user"]

    for sonde in sondes:
        cursor.execute("SELECT timestamp, value FROM system_data WHERE type = ? ORDER BY timestamp", (sonde,))
        data = cursor.fetchall()

        if data:
            dates = [row[0] for row in data]
            valeurs = [row[1] for row in data]

            line_chart = pygal.Line()
            line_chart.title = f'Graphique de la sonde {sonde}'
            line_chart.add(sonde, valeurs)

            output_file = output_dir / f"{sonde}_graph.svg"
            line_chart.render_to_file(output_file)
            print(f"Graphique pour {sonde} enregistré sous {output_file}")

            f.write(f"<h2>Graphique de la sonde {sonde}</h2>\n")
            f.write(f'<object data="/graphs/{os.path.basename(output_file)}" type="image/svg+xml" width="600" height="400"></object>\n')

    f.write("<h2>Tableau des alertes</h2>\n")
    f.write("<table>\n")
    f.write("<tr><th>Date</th><th>ID</th><th>Texte</th><th>Statut</th></tr>\n")

    cursor.execute("SELECT alert_date, alert_id, alert_text, alert_status FROM cert_alerts ORDER BY alert_date DESC")
    alerts = cursor.fetchall()

    if alerts:
        for alert in alerts:
            f.write("<tr>")
            for col in alert:
                f.write(f"<td>{col}</td>")
            f.write("</tr>\n")
    else:
        f.write("<tr><td colspan='4'>Aucune alerte trouvée</td></tr>\n")

    f.write("</table>\n")

    f.write("</body></html>\n")

conn.close()
print(f"Fichier HTML généré à {html_output}")
