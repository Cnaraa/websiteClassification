import pandas as pd
from parser import parse_url
from summarizer import summarize

INPUT_CSV = r"C:\\Study\\Python\\WebsiteClassification\\bot\\filtered_links.csv"
MAX_ARTICLES = 10

def main():
    df = pd.read_csv(INPUT_CSV, on_bad_lines='skip', sep=",", names=["url", "topic"])
    urls = df.to_dict(orient="records")

    count = 0
    for item in urls:
        url = item["url"]
        topic = item["topic"]

        print(f"\nОбрабатываем: {url}")
        article_data = parse_url(url, topic)

        if not article_data:
            continue

        # Генерируем выжимку на основе описания или части текста
        article_data["summary"] = summarize(article_data["full_text"])

        # Сохраняем в БД
        from parser import save_to_db
        save_to_db(article_data)
        print(f"Сохранено в базу: {article_data['title']}")

        count += 1
        if count >= MAX_ARTICLES:
            print(f"Достигнут лимит: {MAX_ARTICLES}")
            break

if __name__ == "__main__":
    main()