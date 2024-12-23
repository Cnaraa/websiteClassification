from get_html import get_yandex_html, get_html, create_driver
from parse_html import get_links, clean_html, get_title_and_description
import csv
import json


def main():
  topics = input().split(',')
  for query in topics:
    driver = create_driver()
    print('Драйвер создан')
    try:
      links = []
      html_content = get_yandex_html(driver, query, 0)
      links.extend(get_links(html_content))
      print(f'Первая страница получена по запросу {query}')
      for page in range(1, 3):
        html_content = get_yandex_html(driver, query, page)
        links.extend(get_links(html_content))
        print(f'Страница {page} обработана')
      data = []
      for url in links:
        html_content = get_html(driver, url)
        print(f'Обработка страницы: {url}')
        get_title_and_description(html_content, url, query)

    finally:
      driver.close()
      driver.quit()


if __name__ == "__main__":
  main()