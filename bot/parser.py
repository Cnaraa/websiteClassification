import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import requests
import re
import time
import random
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename="parser.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

#Проверка безопасности
def is_safe(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        logging.warning(f"Небезопасное соединение: {url}")
        return False
    try:
        response = requests.get(url, timeout=10, verify=True)
        return True
    except Exception as e:
        logging.error(f"Не удалось проверить безопасность {url}: {e}")
        return False

#Очистка HTML
def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script_or_style in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
        script_or_style.decompose()
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

#Извлечение метаданных
def get_head_data(soup):
    title = soup.title.string.strip() if soup.title else "Нет заголовка"
    description = ""
    meta_tags = soup.find_all('meta', attrs={'name': 'description'})
    if meta_tags:
        description = meta_tags[0].get('content', '').strip()
    return title, description

#Сохранение в БД
def save_to_db(data):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    #Автоматическое создание таблицы
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
    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")
    finally:
        conn.close()

#Парсинг одного URL
def parse_url(url, topic):
    PATH = r'C:\Study\Python\WebsiteClassification\bot\chromedriver.exe'
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

    driver = None
    try:
        service = Service(PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        html = driver.page_source
        time.sleep(random.uniform(1, 3))
    except Exception as e:
        logging.error(f"Ошибка при загрузке страницы {url}: {e}")
        return None
    finally:
        if driver:
            driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    title, description = get_head_data(soup)
    is_secure = is_safe(url)
    full_text = clean_html(html)

    result = {
        "url": url,
        "title": title,
        "description": description,
        "full_text": full_text,
        "topic": topic,
        "is_secure": is_secure,
        "timestamp": datetime.now().isoformat()
    }

    return result