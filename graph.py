import sqlite3
import pygal
import os
from pathlib import Path

# Connexion à la base de données
conn = sqlite3.connect("/home/cristiano/projet/ams/monitoring.db")
cursor = conn.cursor()

# Dossier de sortie pour les graphes
output_dir = Path("/home/cristiano/projet/ams/graphs")
output_dir.mkdir(parents=True, exist_ok=True)

# Chemin du fichier HTML de sortie
html_output = output_dir / "graphiques_sondes.html"
with open(html_output, 'w') as f:
    f.write("<html><head><title>Graphiques des sondes</title></head><body>\n")
    f.write("<h1>Graphiques des sondes</h1>\n")
    
    # Liste des sondes
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

            # 👉 Ajout du bon chemin pour Flask
            f.write(f"<h2>Graphique de la sonde {sonde}</h2>\n")
            f.write(f'<object data="/graphs/{os.path.basename(output_file)}" type="image/svg+xml" width="600" height="400"></object>\n')

    f.write("</body></html>\n")

conn.close()
print(f"Fichier HTML généré à {html_output}")
