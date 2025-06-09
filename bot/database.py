# database.py

import sqlite3

def get_all_topics():
    """Возвращает список всех уникальных тем"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT topic FROM articles")
    topics = [t[0] for t in cursor.fetchall()]
    conn.close()
    return topics


def save_to_db(data):
    """Сохраняет статью в БД"""
    conn = sqlite3.connect("data.db")
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

    try:
        cursor.execute("""
        INSERT OR IGNORE INTO articles (url, title, description, summary, topic, is_secure, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["url"],
            data["title"],
            data["description"],
            data["summary"],
            data["topic"],
            data["is_secure"],
            data["timestamp"]
        ))
        conn.commit()
    finally:
        conn.close()