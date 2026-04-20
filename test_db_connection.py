import psycopg2
import os

# Берём параметры из переменных окружения (минуя строку подключения)
os.environ["PGHOST"] = "localhost"
os.environ["PGPORT"] = "5432"
os.environ["PGUSER"] = "postgres"
os.environ["PGPASSWORD"] = "postgres"
os.environ["PGDATABASE"] = "sbs_db"
os.environ["PGCLIENTENCODING"] = "UTF8"

try:
    # Без явной строки подключения!
    conn = psycopg2.connect()
    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")