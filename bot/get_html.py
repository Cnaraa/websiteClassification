import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import logging
import time
import re
import json
import urllib.parse


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-ssl-errors")
    options.add_argument("--headless")  # Режим без графического интерфейса
    logging.getLogger('selenium').setLevel(logging.WARNING)

    PATH = r'C:\\Study\\Python\\WebsiteClassification\\bot\\chromedriver.exe'

    try:
        service = Service(executable_path=PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  # Увеличен таймаут загрузки страницы
        return driver
    except Exception as ex:
        logging.error(f"Не удалось создать драйвер: {ex}")
        raise


def load_page(driver, url, timeout=30):
    try:
        logging.info(f"Загрузка страницы: {url}")
        driver.set_page_load_timeout(timeout)
        driver.get(url)

        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        html_content = driver.page_source
        if not html_content or len(html_content.strip()) == 0:
            logging.warning(f"HTML-код страницы {url} пуст.")
            return None

        return html_content
    except Exception as ex:
        logging.error(f"Ошибка при загрузке страницы {url}: {ex}")
        return None


def get_html(driver, url):
    return load_page(driver, url)