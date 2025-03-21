import psutil

cpu_usage = psutil.cpu_percent(interval=1)
print(f"CPU : {cpu_usage}")

