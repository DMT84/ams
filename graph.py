import sqlite3
import pygal
import os
from pathlib import Path

# Connexion à la base de données
conn = sqlite3.connect("/home/cristiano/projet/ams/monitoring.db")  # Modifie le chemin si nécessaire
cursor = conn.cursor()

# Créer le répertoire dans BASE_PATH au lieu de /mnt/graph (évite les problèmes de permission)
output_dir = Path("/home/cristiano/projet/ams/graphs")
output_dir.mkdir(parents=True, exist_ok=True)  # Crée le répertoire s'il n'existe pas

# Créer un fichier HTML pour inclure les graphiques
html_output = output_dir / "graphiques_sondes.html"
with open(html_output, 'w') as f:
    # Ajouter la structure de base du fichier HTML
    f.write("<html><head><title>Graphiques des sondes</title></head><body>\n")
    f.write("<h1>Graphiques des sondes</h1>\n")
    
    # Liste des sondes à traiter (cpu, disque, user)
    sondes = ["cpu", "disque", "user"]

    # Créer un graphique pour chaque sonde et l'enregistrer dans un fichier SVG
    for sonde in sondes:
        # Récupérer les valeurs de la sonde dans la base de données
        cursor.execute("SELECT timestamp, valeur FROM monitoring WHERE sonde = ?", (sonde,))
        data = cursor.fetchall()
        
        # Extraire les valeurs et les dates pour le graphique
        dates = [row[0] for row in data]  # Liste des timestamps
        valeurs = [row[1] for row in data]  # Liste des valeurs de la sonde
        
        # Créer un graphique de type Line (courbe)
        line_chart = pygal.Line()
        line_chart.title = f'Graphique de la sonde {sonde}'
        
        # Ajouter les données au graphique
        line_chart.add(sonde, valeurs)
        
        # Enregistrer le graphique dans un fichier SVG
        output_file = output_dir / f"{sonde}_graph.svg"
        line_chart.render_to_file(output_file)
        print(f"Graphique pour {sonde} enregistré sous {output_file}")

        # Ajouter le graphique SVG au fichier HTML
        f.write(f"<h2>Graphique de la sonde {sonde}</h2>\n")
        f.write(f'<object data="{os.path.basename(output_file)}" type="image/svg+xml" width="600" height="400"></object>\n')

    # Ajouter la fin du fichier HTML
    f.write("</body></html>\n")

# Fermer la connexion à la base de données
conn.close()

print(f"Fichier HTML généré à {html_output}")
