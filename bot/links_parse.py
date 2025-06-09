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

#Настройки
SEARCH_TOPICS = [
    "Искусственный интеллект и машинное обучение",
    "Компьютерное зрение и распознавание образов",
    "Обработка естественного языка",
    "Фундаментальные основы CS",
    "Криптография и безопасность",
    "Распределённые и параллельные вычисления",
    "Человеко-компьютерное взаимодействие",
    "Компьютеры и общество",
    "Информационный поиск",
    "Робототехника"
]

NUM_PAGES = 15
base_url = "https://ya.ru/search/ "
lr = "213"  #регион: Москва
OUTPUT_FILE = "all_links.csv"

#Список нежелательных доменов
BAD_DOMAINS = {
    #Видео
    'youtube.com', 'youtu.be', 'rutube.ru', 'vimeo.com', 'dailymotion.com',
    #Соцсети
    'vk.com', 'telegram.org', 't.me', 'instagram.com', 'facebook.com',
    'twitter.com', 'x.com', 'ok.ru', 'pinterest.com',
    #Магазины
    'aliexpress.', 'amazon.', 'wildberries', 'ozon.', 'my-shop.', 'labirint.',
    'chitai-gorod.', 'gearbest.', 'market.yandex.', 'shop.', 'store.',
    #Форумы / Блоги
    'wordpress.'
    #Реклама / трекеры
    'taboola', 'yabs.', 'clck.', 'ad.mail.ru', 'googleadservices.',
    #Новости / медиа
    'news', 'gazeta.', 'lenta.', 'kommersant.', 'rbc.', 'forbes.', '161.ru',
    #Прочее
    'telegram.', 'gov.ru', 'student.zoomru.ru', 'nikulya.'
}

#Создание папок
if not os.path.exists("collected_links"):
    os.makedirs("collected_links")

#Настройки Selenium
def setup_browser():
    PATH = r'C:\Study\Python\WebsiteClassification\bot\chromedriver.exe'
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    #Антибот-защита
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(executable_path=PATH)
    driver = webdriver.Chrome(service=service, options=options)

    #Скрываем следы автоматизации
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

#Генерация случайной паузы
def random_pause(min_sec=5, max_sec=8):
    pause = random.uniform(min_sec, max_sec)
    print(f"Пауза {pause:.2f} секунд...")
    time.sleep(pause)

#Ожидание решения CAPTCHA вручную
def wait_for_captcha(driver):
    try:
        print("🔍 Проверяем наличие CAPTCHA...")
        captcha_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Подтвердите, что вы не робот")]'))
        )
        if captcha_element:
            print("Обнаружена CAPTCHA. Подтвердите, что вы не робот.")
            input("Нажмите Enter после прохождения CAPTCHA...")

            #Ждём продолжения загрузки результатов
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li.serp-item_card[data-fast="1"]'))
            )
            print("Продолжаем работу после CAPTCHA")
            return True
    except Exception as e:
        print("CAPTCHA не найдена — продолжаем автоматически")
        return False

#Парсинг страницы выдачи
def parse_yandex_results(html, topic):
    soup = BeautifulSoup(html, 'html.parser')
    links = []

    items = soup.select('li.serp-item_card[data-fast="1"]')
    for item in items:
        try:
            link_tag = item.select_one('a.link')
            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href']

                # Проверяем, содержит ли ссылка BAD_DOMAIN
                if any(domain in link for domain in BAD_DOMAINS):
                    print(f"Пропущена ссылка: {link} (недопустимый домен)")
                    continue

                if link.startswith("https://"):
                    links.append({"url": link, "topic": topic})
        except Exception as e:
            print(f"Ошибка при парсинге элемента: {e}")
            continue

    return links

#Сбор ссылок по одной запросу
def collect_links(query, num_pages=5, lr="213"):
    driver = setup_browser()
    collected_data = []

    try:
        for page in range(num_pages):
            url = f"{base_url}?text={query}&lr={lr}&p={page}"
            print(f"\n--- Тема: '{query}' | Страница {page + 1}: {url}")

            driver.get(url)

            # Ждём появления карточек
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li.serp-item_card'))
                )

                wait_for_captcha(driver)

                html = driver.page_source
                new_links = parse_yandex_results(html, query.replace(" ", "_"))
                print(f"Найдено ссылок на странице: {len(new_links)}")

                collected_data.extend(new_links)

            except Exception as e:
                print(f"Не удалось загрузить страницу {page + 1}: {e}")

            random_pause(5, 8)

    finally:
        driver.quit()

    #Добавление данных в общий файл
    df_new = pd.DataFrame(collected_data)

    if os.path.exists(OUTPUT_FILE):
        df_old = pd.read_csv(OUTPUT_FILE)
        old_urls = set(df_old['url'].values)
        df_new = df_new[~df_new['url'].isin(old_urls)]
        print(f"Найдены дубликаты — пропускаем {len(collected_data) - len(df_new)} ссылок")
    else:
        print("Создаётся новый файл")

    if not df_new.empty:
        df_new.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig", mode='a', header=not os.path.exists(OUTPUT_FILE))
        print(f"Добавлено новых ссылок: {len(df_new)}")
    else:
        print("Новых ссылок для добавления нет.")

#Запуск сбора по всем темам
if __name__ == "__main__":
    seen_urls = set()

    for topic in SEARCH_TOPICS:
        print(f"\nНачинаем сбор по теме: {topic}")
        collect_links(topic, num_pages=NUM_PAGES, lr=lr)