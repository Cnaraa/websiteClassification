import sqlite3
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from datetime import datetime
from summarizer import summarize
import trafilatura
import logging
import warnings
import os
from langdetect import detect
from timeout_decorator import timeout

# Настройки логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Подавление предупреждений
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Путь к chromedriver
PATH = r'C:\Study\Python\WebsiteClassification\bot\chromedriver.exe'

# Проверка на безопасность
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


# Настройка БД
DB_PATH = r'C:\Study\Python\WebsiteClassification\bot\data.db'



def save_to_db(data):
    """
    Сохраняет результат в базу данных по заданным правилам.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Применяем правила заполнения description и summary
        description = data['description'] if data['description'] else "Нет данных"
        summary = data['summary'] if data['summary'] else "Нет данных"

        try:
            cursor.execute('''
                INSERT INTO articles 
                (url, title, description, summary, topic, is_secure, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                data['url'],
                data['title'],
                description,
                summary,
                data['topic'],
                data['is_secure']
            ))
            conn.commit()
            logging.info(f"Данные успешно сохранены для {data['url']}")
        except sqlite3.IntegrityError:
            logging.warning(f"URL уже существует в базе: {data['url']}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении в БД: {e}")

def is_custom_404(title, full_text):
    """Проверяет, является ли страница кастомной 404"""
    keywords = [
        '404', 'not found', 'страница не найдена', 'page not found',
        'ничего не найдено', 'запрашиваемая страница не существует',
        'ошибка 404', 'не установлены сертификаты', 'минцифры', 'проблема при открытии сайта',
        'support id'
    ]
    combined = (title + " " + full_text).lower() if title and full_text else ""
    for keyword in keywords:
        if keyword in combined:
            return True
    return False


def is_captcha_page(title, full_text, html):
    """Проверяет, является ли страница капчей"""
    # Объединяем заголовок и текст для поиска ключевых слов
    combined = (title or "") + " " + (full_text or "")
    combined = combined.lower()

    # Ключевые слова, связанные с капчей
    captcha_keywords = [
        'captcha', 'reCAPTCHA','recaptcha', 'not a robot', 'security check', 'human verification', 'капча',
        'обратитесь по номеру', 'позвоните нам', 'сообщите нам', 'я не робот', 'подозрительный трафик', 'smartcaptcha', 'отключено исполнение JavaScript', 'похожи на автоматические'
    ]

    # Проверяем наличие хотя бы одного ключевого слова
    for keyword in captcha_keywords:
        if keyword in combined:
            return True

    # Дополнительно проверяем HTML на наличие iframe с reCAPTCHA
    if 'src="https://www.google.com/recaptcha/'  in html:
        return True

    return False

def get_status_code(url):
    try:
        response = requests.get(url, timeout=10, verify=True)
        return response.status_code
    except:
        return None

def is_russian_text(text):
    try:
        # Берём первые 500 символов для повышения скорости и точности
        sample = text[:500]
        lang = detect(sample)
        return lang == 'ru'
    except Exception as e:
        logging.warning(f"Не удалось определить язык: {e}")
        return False


def parse_page(url, topic, timeout=40, driver=None, save_to_db=True):
    if not save_to_db:
        existing_record = url_exists_in_db(url, check=False)
        if existing_record:
            logging.info(f"Запись найдена в БД для {url}")
            keys = ['id', 'url', 'title', 'description', 'summary', 'topic', 'is_secure', 'timestamp']
            result = dict(zip(keys, existing_record))
            return result
    else:
        if url_exists_in_db(url):
            logging.warning(f"URL уже существует в базе: {url}. Пропускаем.")
            return None
    
    status_code = get_status_code(url)
    if status_code == 404:
        logging.warning(f"Получен статус-код 404 для {url}. Страница пропущена.")
        return None

    own_driver = False
    driver = None

    try:
        # Подключение к странице через Selenium
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')
        service = Service(executable_path=PATH)
        driver = webdriver.Chrome(service=service, options=options)
        own_driver = True

        logging.info(f"Переход по ссылке: {url}")
        driver.get(url)

        logging.info(f"Ожидание загрузки страницы до 40 секунд...")
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        title_tag = soup.title
        title = title_tag.string.strip() if title_tag and title_tag.string else None

        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag and 'content' in description_tag.attrs else None

        clean_text = trafilatura.extract(html)

        if not clean_text or len(clean_text.split()) < 15:
            logging.warning(f"На странице слишком мало текста для анализа: {url}")
            return None

        if not is_russian_text(clean_text):
            logging.warning(f"Страница не на русском языке: {url}. Пропускаем.")
            return None

        if is_captcha_page(title, clean_text, html):
            logging.warning(f"Обнаружена капча на странице: {url}. Страница пропущена.")
            return None

        if is_custom_404(title, clean_text):
            logging.warning(f"Обнаружена страница 404: {url}. Страница пропущена.")
            return None

        summary = summarize(clean_text) if clean_text else None

        if summary is None:
            summary = "Нет данных"
        if description is None:
            description = "Нет данных"
        if description == summary:
            return None

        result = {
            'url': url,
            'title': title,
            'description': description,
            'summary': summary,
            'topic': topic,
            'is_secure': is_safe(url),
        }

        if save_to_db:
            save_to_db(result)

        return result

    except TimeoutException:
        logging.error("Ошибка: Превышено время ожидания загрузки страницы.")
    except WebDriverException as e:
        logging.error(f"Ошибка веб-драйвера: {e}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
    finally:
        if own_driver and driver:
            driver.quit()

    return None


def url_exists_in_db(url, check=True):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
        exists = cursor.fetchone() is not None

        if not check and exists:
            cursor.execute("SELECT * FROM articles WHERE url = ?", (url,))
            return cursor.fetchone()
        return exists


# Пример использования
if __name__ == "__main__":
    url = input("Введите URL научной статьи: ")
    topic = input("Введите тему статьи: ")
    result = parse_page(url, topic)

    if result:
        print("\nTitle:", result['title'] or "Не найдено")
        print("Description:", result['description'] or "Нет данных")
        print("Summary:")
        print(result['summary'] or "Невозможно сгенерировать выжимку")
    else:
        print("Не удалось получить данные.")