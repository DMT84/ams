from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# 👉 Sert le fichier HTML principal
@app.route('/')
def afficher_graphiques():
    return send_from_directory('graphs', 'graphiques_sondes.html')

# 👉 Sert les fichiers SVG depuis le dossier 'graphs'
@app.route('/graphs/<path:filename>')
def servir_graph(filename):
    return send_from_directory('graphs', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
