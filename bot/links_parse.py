from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import os

# Настройки
SEARCH_QUERIES = [
    {
        "topic": "Компьютерное зрение и распознавание образов",
        "queries": [
            "Компьютерное зрение и распознавание образов",
            "основные методы и алгоритмы компьютерного зрения"
        ]
    },
    {
        "topic": "Фундаментальные основы CS",
        "queries": [
            "Фундаментальные основы computer science",
            "алгоритмы, структуры данных и вычислительная сложность"
        ]
    },
    {
        "topic": "Криптография и безопасность информации",
        "queries": [
            "Криптография и безопасность информации",
            "методы шифрования и защиты данных в цифровой среде"
        ]
    },
    {
        "topic": "Компьютеры и общество",
        "queries": [
            "Компьютеры и общество",
            "этические и правовые вопросы цифровизации общества"
        ]
    },
    {
        "topic": "Искусственный интеллект и машинное обучение",
        "queries": [
            "Искусственный интеллект и машинное обучение",
            "как работают алгоритмы машинного обучения и где они применяются"
        ]
    },
    {
        "topic": "Обработка естественного языка",
        "queries": [
            "Обработка естественного языка",
            "применение NLP в реальных задачах анализа текста"
        ]
    },
    {
        "topic": "Распределённые и параллельные вычисления",
        "queries": [
            "Распределённые и параллельные вычисления",
            "архитектура систем с распределённой обработкой данных"
        ]
    },
    {
        "topic": "Робототехника",
        "queries": [
            "Робототехника",
            "роботы и их применение в промышленности и быту"
        ]
    },
    {
        "topic": "Информационный поиск",
        "queries": [
            "Информационный поиск",
            "алгоритмы ранжирования и индексации в поисковых системах"
        ]
    },
    {
        "topic": "Человеко-компьютерное взаимодействие",
        "queries": [
            "Человеко-компьютерное взаимодействие",
            "оценка удобства и эффективности взаимодействия с программным обеспечением"
        ]
    }
]

NUM_PAGES = 5
base_url = "https://ya.ru/search/" 
lr = "213"  # регион: Москва
OUTPUT_FILE = "all_links.csv"

#Нежелательные домены
BAD_DOMAINS = {
    'youtube.com', 'youtu.be', 'rutube.ru', 'vimeo.com', 'dailymotion.com',
    'vk.com', 'telegram.org', 't.me', 'instagram.com', 'facebook.com',
    'twitter.com', 'x.com', 'ok.ru', 'pinterest.com',
    'aliexpress.', 'amazon.', 'wildberries', 'ozon.', 'my-shop.ru', 'labirint.',
    'chitai-gorod.', 'gearbest.', 'market.yandex.', 'shop.', 'store.',
    'blogspot.', 'livejournal.', 'habr.', 'medium.', 'tumblr.', 'wordpress.',
    'taboola', 'yabs.', 'clck.', 'ad.mail.ru', 'googleadservices.',
    'news', 'gazeta.', 'lenta.', 'kommersant.', 'rbc.', 'forbes.', '161.ru',
    'wikiwand.', 'telegram.', 'gov.ru', 'student.zoomru.ru', 'nikulya.ru', 'koriolan404.narod.ru', 'monoreel.ru',
    'gpntb.ru', 'lab314.brsu.by', 'toglht.ru', 'profbeckman.narod.ru', 'fips.'
}

#Настройки Selenium
def setup_browser():
    PATH = r'C:\Study\Python\WebsiteClassification\bot\chromedriver.exe'
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36")

    # Антибот-защита
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(executable_path=PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # Скрываем следы автоматизации
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


#Генерация случайной паузы
def random_pause(min_sec=1, max_sec=2):
    pause = random.uniform(min_sec, max_sec)
    print(f"Пауза {pause:.2f} секунд...")
    time.sleep(pause)


#Ожидание решения капчи вручную
def wait_for_captcha(driver):
    try:
        print("Проверяем наличие капчи")
        captcha_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Подтвердите, что вы не робот")]'))
        )
        if captcha_element:
            print("Обнаружена Капча.")

            # Ждём продолжения загрузки результатов
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li.serp-item_card[data-fast="1"]'))
            )
            print("Продолжаем работу после Капча")
            return True
    except Exception as e:
        print("Капча не найдена")
        return False


# Парсинг страницы выдачи
def parse_yandex_results(html, topic_label):
    soup = BeautifulSoup(html, 'html.parser')
    links = []

    items = soup.select('li.serp-item_card[data-fast="1"]')
    for item in items:
        try:
            link_tag = item.select_one('a.link')
            if not link_tag or 'href' not in link_tag.attrs:
                continue

            link = link_tag['href']

            # Фильтр по доменам
            if any(domain in link for domain in BAD_DOMAINS):
                print(f"Пропущена ссылка: {link} (недопустимый домен)")
                continue

            if not link.startswith("https://"): 
                continue

            links.append({"url": link, "topic": topic_label})

        except Exception as e:
            print(f"Ошибка при парсинге элемента: {e}")
            continue

    return links


#Сбор ссылок по одной поисковой фразе
def collect_links(query, topic_label, num_pages=5, lr="213"):
    driver = setup_browser()
    collected_data = []

    try:
        for page in range(num_pages):
            url = f"{base_url}?text={query}&lr={lr}&p={page}"
            print(f"\n--- Запрос: '{query}' | Страница {page + 1}: {url}")

            driver.get(url)

            #Ждём появления карточек
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li.serp-item_card'))
                )

                #Если есть капча — ждём решения
                wait_for_captcha(driver)

                html = driver.page_source
                new_links = parse_yandex_results(html, topic_label)
                print(f"Найдено ссылок на странице: {len(new_links)}")
                collected_data.extend(new_links)

            except Exception as e:
                print(f"Не удалось загрузить страницу {page + 1}: {e}")

            random_pause(5, 8)

    finally:
        driver.quit()

    #Сохранение в CSV
    df_new = pd.DataFrame(collected_data)

    if os.path.exists(OUTPUT_FILE):
        df_old = pd.read_csv(OUTPUT_FILE)
        seen_pairs = set(zip(df_old["url"], df_old["topic"]))
        df_new = df_new[~df_new.apply(lambda row: (row["url"], row["topic"]) in seen_pairs, axis=1)]
        print(f"Осталось: {len(df_new)} уникальных ссылок")
    else:
        print("Создаётся новый файл")

    if not df_new.empty:
        df_new.to_csv(OUTPUT_FILE, index=False, mode='a', header=not os.path.exists(OUTPUT_FILE), encoding="utf-8-sig")
        print(f"Добавлено новых ссылок: {len(df_new)}")
    else:
        print("Новых ссылок для добавления нет.")


#Запуск сбора по всем темам
if __name__ == "__main__":
    for entry in SEARCH_QUERIES:
        topic_label = entry["topic"]
        queries = entry["queries"]

        print(f"\nНачинаем сбор по теме: {topic_label}")
        for query in queries:
            print(f"Выполняется поиск: '{query}'")
            collect_links(query=query, topic_label=topic_label, num_pages=NUM_PAGES, lr=lr)