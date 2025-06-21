import csv
import time
import logging
import itertools
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from parser import url_exists_in_db, parse_page

# Настройки логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Путь к chromedriver
CHROMEDRIVER_PATH = r'C:\Study\Python\WebsiteClassification\bot\chromedriver.exe'
CSV_PATH = r'C:\Study\Python\WebsiteClassification\all_links.csv'
DELAY_BETWEEN_REQUESTS = 0.25


def batch_parse(csv_path):
    rows = []
    with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
        content = csvfile.read()
        lines = content.strip().split('\n')
        for line in lines:
            if ',' in line:
                parts = line.split(',')
                url_part = ','.join(parts[:-1]).strip()
                topic = parts[-1].strip()
                if url_part and topic:
                    rows.append({'url': url_part, 'topic': topic})

    total = len(rows)
    logging.info(f"Начинаем обработку. Всего: {total} ссылок.")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--user-agent=Mozilla/5.0 ... Chrome/137.0.0.0 Safari/537.36')
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for idx, row in enumerate(rows, start=1):
            url = row.get('url')
            topic = row.get('topic')

            if not url or not topic:
                logging.warning(f"[{idx}/{total}] Некорректная строка в CSV: {row}")
                continue

            if url_exists_in_db(url):
                logging.warning(f"[{idx}/{total}] URL уже существует в базе: {url}. Пропускаем.")
                continue

            try:
                # Открываем новую вкладку, кроме первой
                if idx > 1:
                    driver.execute_script("window.open('');")
                    handles = driver.window_handles
                    driver.switch_to.window(handles[-1])

                result = parse_page(url, topic, driver=driver)

                # Закрываем вкладку, если она была создана
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                if result:
                    logging.info(f"[{idx}/{total}] Успешно обработано: {url}")
                else:
                    logging.warning(f"[{idx}/{total}] Не удалось обработать: {url}")

            except Exception as e:
                logging.error(f"[{idx}/{total}] Ошибка при обработке {url}: {e}")
            finally:
                time.sleep(DELAY_BETWEEN_REQUESTS)

    finally:
        driver.quit()
        logging.info("Браузер полностью закрыт.")


if __name__ == "__main__":
    batch_parse(CSV_PATH)