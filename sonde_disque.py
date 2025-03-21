import psutil

disk_usage = psutil.disk_usage('/').percent
print(f"Disque : {disk_usage}")

