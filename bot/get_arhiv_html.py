import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from bs4.element import Comment
import logging
import time
import re
import json
import urllib.parse
import html
from lxml import html as lxml_html
import pandas as pd


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


def get_html(driver, url):
  try:
    driver.get(url)
    time.sleep(3)
    html_content = driver.page_source
  except Exception as ex:
    print(ex)
  
  return html_content


def parse_html(html_content):
  articles = []
  soup = BeautifulSoup(html_content, "html.parser")
  nav_block = soup.find('nav', attrs={"aria-label": "pagination"})
  next_page = nav_block.find('a', class_="pagination-next")
  if "disabled" in next_page.attrs or "is-invisible" in next_page.get("class", []):
    next_button = False
  else:
    next_button = True
  cards = soup.find_all("li", class_="arxiv-result")
  for element in cards:
    title = element.find('p', class_='title is-5 mathjax').get_text(strip=True)
    summary = element.find('span', class_='abstract-full has-text-grey-dark mathjax').get_text(strip=True)
    categories = []
    spans = element.find('div', class_='tags is-inline-block').find_all("span", attrs={"data-tooltip": True})
    for span in spans:
      category = span.get("data-tooltip")
      categories.append(category) 
    articles.append({
                    "title": title,
                    "summary": summary[:-6],
                    "categories": categories
                    })
  
  return articles, next_button



def main():
  driver = create_driver()
  print('Драйвер создан')
  categories = [
    "cs.AI",  # Artificial Intelligence
    "cs.AR",  # Hardware Architecture
    "cs.CC",  # Computational Complexity
    "cs.CE",  # Computational Engineering, Finance, and Science
    "cs.CG",  # Computational Geometry
    "cs.CL",  # Computation and Language (Natural Language Processing)
    "cs.CR",  # Cryptography and Security
    "cs.CV",  # Computer Vision and Pattern Recognition
    "cs.CY",  # Computers and Society
    "cs.DB",  # Databases
    "cs.DC",  # Distributed, Parallel, and Cluster Computing
    "cs.DL",  # Digital Libraries
    "cs.DM",  # Discrete Mathematics
    "cs.DS",  # Data Structures and Algorithms
    "cs.ET",  # Emerging Technologies
    "cs.FL",  # Formal Languages and Automata Theory
    "cs.GL",  # General Literature (e.g., introductory material)
    "cs.GR",  # Graphics
    "cs.GT",  # Computer Science and Game Theory
    "cs.HC",  # Human-Computer Interaction
    "cs.IR",  # Information Retrieval
    "cs.IT",  # Information Theory
    "cs.LG",  # Machine Learning
    "cs.LO",  # Logic in Computer Science
    "cs.MA",  # Multiagent Systems
    "cs.MM",  # Multimedia
    "cs.MS",  # Mathematical Software
    "cs.NA",  # Numerical Analysis
    "cs.NE",  # Neural and Evolutionary Computing
    "cs.NI",  # Networking and Internet Architecture
    "cs.OH",  # Other Computer Science (miscellaneous topics)
    "cs.OS",  # Operating Systems
    "cs.PF",  # Performance
    "cs.PL",  # Programming Languages
    "cs.RO",  # Robotics
    "cs.SC",  # Symbolic Computation
    "cs.SD",  # Sound
    "cs.SE",  # Software Engineering
    "cs.SI",  # Social and Information Networks
    "cs.SY"   # Systems and Control
]
  try:
    for category in categories:
      filename = f'arxiv_{category}_articles.csv'
      data = []
      for step in range(0, 10000, 200):
        url = f'https://arxiv.org/search/?searchtype=all&query={category}&abstracts=show&size=200&order=-announced_date_first&start={step}'
        html_content = get_html(driver, url)
        articles, next_button = parse_html(html_content)
        data.extend(articles)
        print(f'Обработано {len(data)} статей для категории: {category}')
        if next_button is False:
          print(f'Обработана последняя страница для категории: {category}')
          break

      df = pd.DataFrame(data)
      df.to_csv(filename, index=False, encoding="utf-8")
      print(f"Data saved to '{filename}'")

  finally:
    driver.close()
    driver.quit()


if __name__ == "__main__":
  main()