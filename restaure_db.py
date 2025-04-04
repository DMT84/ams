import shutil
import os

BASE_PATH = "/home/cristiano/projet/ams"
DB_PATH = os.path.join(BASE_PATH, "monitoring.db")
BACKUP_PATH = os.path.join(BASE_PATH, "monitoring_backup.db")

def restore_database():
    if os.path.exists(BACKUP_PATH):
        try:
            shutil.copy2(BACKUP_PATH, DB_PATH)
            print(f"Base restaurée depuis {BACKUP_PATH}")
        except Exception as e:
            print(f"Erreur restauration DB: {e}")
    else:
        print("Aucun backup trouvé pour restaurer.")

if __name__ == "__main__":
    restore_database()
