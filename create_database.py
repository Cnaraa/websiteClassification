import sqlite3

DB_NAME = "data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        title TEXT,
        description TEXT,
        summary TEXT,
        topic TEXT,
        is_secure BOOLEAN,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()
    print(f"База данных {DB_NAME} готова")

if __name__ == "__main__":
    init_db()