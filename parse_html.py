from bs4 import BeautifulSoup
from bs4.element import Comment
import re
import html
from lxml import html as lxml_html
from get_html import get_html
import json


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


def get_title_and_description(html_content, url, query):
    soup = BeautifulSoup(html_content, "html.parser")
    language = soup.html.get('lang')
    
    if language == 'ru':
        try:
            description = soup.find('meta', attrs={'name': 'description'})
            if description:
                description_text = description['content'].strip()
            else:
                description_text = None
        except:
            print('Ошибка при получении описания')
            description_text = None

        try:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
            else:
                title = None
        except:
            print('Ошибка при получении заголовка')
            title = None

        save_to_file(title, description_text, url, query)
        return title, description_text
    else:
        return False, False

def save_to_file(title, description, url, query):
  data = {'title': title, 'description': description, 'url' : url, 'label': query}
  filename = "output.json"
    
  with open(filename, 'a+', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.write('\n')

  print(f"Данные сохранены в файл {filename}.")
  return True