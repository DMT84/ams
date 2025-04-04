import sqlite3
import pygal
import os
from pathlib import Path

conn = sqlite3.connect("/home/cristiano/projet/ams/monitoring.db")  # Modifie le chemin selon ton installation
cursor = conn.cursor()

output_dir = Path("/mnt/graph")
output_dir.mkdir(parents=True, exist_ok=True)

html_output = output_dir / "graphiques_sondes.html"
with open(html_output, 'w') as f:
    # Ajouter la structure de base du fichier HTML
    f.write("<html><head><title>Graphiques des sondes</title></head><body>\n")
    f.write("<h1>Graphiques des sondes</h1>\n")
    
    sondes = ["cpu", "disque", "user"]

    for sonde in sondes:
        # Récupérer les valeurs de la sonde dans la base de données
        cursor.execute("SELECT timestamp, valeur FROM monitoring WHERE sonde = ?", (sonde,))
        data = cursor.fetchall()
        
        dates = [row[0] for row in data]  # Liste des timestamps
        valeurs = [row[1] for row in data]  # Liste des valeurs de la sonde
        
        line_chart = pygal.Line()
        line_chart.title = f'Graphique de la sonde {sonde}'
        
        line_chart.add(sonde, valeurs)
        
        output_file = output_dir / f"{sonde}_graph.svg"
        line_chart.render_to_file(output_file)
        print(f"Graphique pour {sonde} enregistré sous {output_file}")

        f.write(f"<h2>Graphique de la sonde {sonde}</h2>\n")
        f.write(f'<object data="{os.path.basename(output_file)}" type="image/svg+xml" width="600" height="400"></object>\n')

    f.write("</body></html>\n")

conn.close()

print(f"Fichier HTML généré à {html_output}")
