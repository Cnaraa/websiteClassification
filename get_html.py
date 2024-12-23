import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
  options.add_argument("--headless")
  logging.getLogger('selenium').setLevel(logging.WARNING)

  PATH = ''


  s = Service(executable_path=PATH)
  driver = webdriver.Chrome(service=s, options=options)

  return driver


def get_yandex_html(driver, query, page):

  encoded_query = urllib.parse.quote(query)
  url = f"https://yandex.ru/search/?text={encoded_query}&p={str(page)}"

  try:
    driver.get(url)
    time.sleep(10)
    html_content = driver.page_source
  except Exception as ex:
    print(ex)
  
  return html_content


def get_html(driver, url):
  try:
    driver.get(url)
    time.sleep(5)
    html_content = driver.page_source
  except Exception as ex:
    print(ex)
  
  return html_content