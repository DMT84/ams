from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def afficher_graphiques():
    # Renvoie le fichier HTML généré dans 'static/'
    return send_from_directory('graphs', 'graphiques_sondes.html')

if __name__ == '__main__':
    # Active le mode débogage pour avoir plus de détails sur les erreurs
    app.run(host='0.0.0.0', port=7777, debug=True)
