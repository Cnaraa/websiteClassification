from bs4 import BeautifulSoup
from bs4.element import Comment
import re
import html
from lxml import html as lxml_html
from get_html import get_html
import json
import logging


def get_links(html_content):
  links = []
  soup = BeautifulSoup(html_content, "html.parser")
  elements = soup.find_all("li", class_="serp-item serp-item_card", attrs={"data-fast": "1"})

  for card in elements:
    card = lxml_html.fromstring(str(card))
    link = card.xpath('div/div[1]/a/@href')
    if link:
      links.extend(link)
  
  return links


def clean_html(html_content):
  soup = BeautifulSoup(html_content, "html.parser")
  for tag in soup(["script", "style", "meta", "link", "iframe", "noscript"]):
    tag.decompose()
  for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
    comment.extract()
  text = soup.get_text(separator=" ", strip=True)
  text = html.unescape(text)
  text = re.sub(r'\s+', ' ', text).strip()
  
  return text


def get_title_and_description(html_content, url, query=None):
    soup = BeautifulSoup(html_content, "html.parser")

    try:
        # Извлекаем заголовок
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else None
    except Exception as ex:
        logging.error(f"Ошибка при получении заголовка: {ex}")
        title = None

    try:
        # Извлекаем описание
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag else None
    except Exception as ex:
        logging.error(f"Ошибка при получении описания: {ex}")
        description = None

    return title, description

def save_to_file(title, description, url, query):
  data = {'title': title, 'description': description, 'url' : url, 'label': query}
  filename = "output.json"
    
  with open(filename, 'a+', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.write('\n')

  print(f"Данные сохранены в файл {filename}.")
  return True