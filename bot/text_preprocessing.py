import re
from nltk.corpus import stopwords
from pymystem3 import Mystem

mystem = Mystem()
stop_words = set(stopwords.words('russian'))
cached_lemmatize = {}

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^а-яёa-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [word for word in text.split() if word not in stop_words]

    def lemmatize_word(word):
        if word in cached_lemmatize:
            return cached_lemmatize[word]
        if re.match(r'^[а-яё]+$', word):
            lemma = mystem.lemmatize(word)[0]
            cached_lemmatize[word] = lemma
            return lemma
        return word

    lemmas = [lemmatize_word(word) for word in words]
    
    return " ".join(lemmas).strip()