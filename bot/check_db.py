import sqlite3
import pandas as pd

# Подключаемся к БД
conn = sqlite3.connect("data.db")

# Загружаем таблицу в DataFrame
query = "SELECT * FROM articles"
df = pd.read_sql_query(query, conn)

# Выводим первые N строк
print(f"Всего записей в базе: {len(df)}")
print("\nПервые 5 статей:")
print(df.head(5))