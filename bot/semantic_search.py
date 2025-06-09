from sentence_transformers import SentenceTransformer, util
import sqlite3
import torch

#Инициализация модели
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def load_all_articles():
    """Загружает все статьи из БД"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, description, summary, topic FROM articles")
    rows = cursor.fetchall()
    conn.close()

    articles = []
    for row in rows:
        url, title, description, summary, topic = row
        combined_text = f"{title} {description} {summary}"
        articles.append({
            "url": url,
            "title": title,
            "description": description,
            "summary": summary,
            "topic": topic,
            "text": combined_text
        })
    return articles


def build_embeddings(articles):
    print("Генерируем эмбеддинги...")
    texts = [a["text"] for a in articles]
    embeddings = model.encode(texts, convert_to_tensor=True)
    return articles, embeddings


def search(query, articles, embeddings, top_k=5):
    query_emb = model.encode([query], convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, embeddings)[0]
    top_indices = torch.topk(cos_scores, k=top_k).indices.tolist()

    results = [articles[i] for i in top_indices]
    return results