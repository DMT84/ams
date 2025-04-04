import shutil
import os

BASE_PATH = "/home/cristiano/projet/ams"
DB_PATH = os.path.join(BASE_PATH, "monitoring.db")
BACKUP_PATH = os.path.join(BASE_PATH, "monitoring_backup.db")

def backup_database():
    try:
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"Base de données sauvegardée sous {BACKUP_PATH}")
    except Exception as e:
        print(f"Erreur sauvegarde DB: {e}")

if __name__ == "__main__":
    backup_database()
