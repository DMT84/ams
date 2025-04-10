# Projet de Monitoring de Système

## Présentation

Ce projet a pour objectif de développer une plateforme de surveillance d'un parc informatique. Il permet à l'administrateur système de surveiller en temps réel l'état des serveurs et de recevoir des alertes en cas de situations critiques, telles que :

- Serveur inactif depuis plus de 30 minutes.
- Disque dur plein à 100%.
- Utilisation de la RAM à 100%.

Le projet est écrit en Bash et Python et utilise différentes librairies comme `psutil`, `sqlite3`, `pygal`, et `Flask` pour la collecte, le stockage des données, l'alerte par email et l'affichage des graphiques de performance.

## Fonctionnalités

Le projet est composé de plusieurs éléments interconnectés, permettant d'assurer une surveillance continue et des alertes en temps réel.

### 1. **Collecte des données**

La collecte des données se fait à intervalles réguliers (toutes les 1 à 5 minutes) à partir de sondes installées sur les serveurs à surveiller. Les informations collectées comprennent des métriques telles que :

- L'utilisation du CPU
- L'utilisation du disque
- Le nombre d'utilisateurs connectés

### 2. **Stockage et archivage**

Les données collectées sont stockées dans une base de données SQLite (`monitoring.db`). Le gestionnaire de stockage :

- Gère l'historique des données collectées.
- Supprime les anciennes données (plus de 7 jours).
- Récupère les alertes CERT et les enregistre dans la base.

### 3. **Alertes par email**

Un système d'alertes est mis en place pour prévenir l'administrateur par email si un seuil critique est atteint (par exemple, 90% d'utilisation CPU). Les alertes sont envoyées à l'adresse définie dans la configuration avec un message formaté à partir d'un template.

### 4. **Affichage des graphiques**

Les données collectées sont également présentées sous forme de graphiques pour faciliter la visualisation des performances du système :

- Un graphique pour chaque sonde (CPU, disque, utilisateurs).
- Un tableau affichant les alertes CERT récupérées.

Les graphiques sont générés en format SVG et sont affichés via une interface web.

### 5. **Interface Web**

Une interface web développée avec Flask permet de consulter les graphiques des sondes et les alertes CERT. Elle est accessible via `http://localhost:5000`.

## Installation et Utilisation

### 1. **Prérequis**

- Python 3.x
- Bibliothèques Python :
  - `psutil`
  - `pygal`
  - `requests`
  - `flask`
  - `beautifulsoup4`
- Serveur SMTP pour l'envoi d'emails (configuré dans `checks_alerts.py`).

### 2. **Installation des dépendances**

```bash
pip install psutil pygal requests flask beautifulsoup4

3. Initialisation de la base de données

Avant de démarrer le projet, vous devez initialiser la base de données :

python init_db.py

4. Exécution de la collecte des données

Pour collecter les données des sondes, vous pouvez lancer le script principal :

python collect.py

Ce script effectuera les actions suivantes :

    Collecte des données des sondes (CPU, disque, utilisateurs).

    Sauvegarde de la base de données.

    Vérification des alertes et envoi de mails si des seuils sont atteints.

5. Affichage des graphiques

Pour visualiser les graphiques des sondes, lancez l'interface web avec Flask :

python web.py

Puis, ouvrez un navigateur et accédez à http://localhost:5000 pour voir les graphiques générés.
6. Restauration de la base de données

Si nécessaire, vous pouvez restaurer la base de données à partir d'un backup :

python restaure_db.py

7. Nettoyage des anciennes données

Pour supprimer les données plus anciennes que 7 jours, exécutez :

python clean_data.py

Structure des Fichiers

Voici la structure des fichiers du projet :

/projet/
├── collect.py            # Script principal de collecte des données
├── init_db.py            # Script d'initialisation de la base de données
├── checks_alerts.py      # Script de vérification des alertes et envoi d'emails
├── clean_data.py         # Script de nettoyage des anciennes données
├── graph.py              # Générateur de graphiques des sondes
├── web.py                # Interface web Flask pour afficher les graphiques
├── config.json           # Fichier de configuration des sondes
├── monitoring.db         # Base de données SQLite
├── monitoring_backup.db  # Backup de la base de données
├── template.txt          # Template pour les emails d'alerte
├── sonde_cpu.py          # Script de collecte des données CPU
├── sonde_disque.py       # Script de collecte des données disque
├── sonde_user.sh         # Script de collecte des données utilisateurs
├── restaure_db.py        # Script de restauration de la base de données
└── README.md             # Ce fichier

Conclusion

Ce projet est conçu pour fournir une solution robuste et flexible de surveillance d'un parc informatique. Il permet de collecter et stocker des données système critiques, d'envoyer des alertes par email et de visualiser les performances via une interface web.

N'hésitez pas à personnaliser le projet selon vos besoins et à ajouter de nouvelles sondes ou fonctionnalités !
