import pandas as pd

df = pd.read_csv('arhiv_data.csv')
df = df.drop_duplicates(subset='title', keep='first')
df = df.drop_duplicates(subset='summary', keep='first')
df = df.dropna(subset=['title'])
df = df.dropna(subset=['summary'])

df.to_csv('arhiv_data.csv', index=False, encoding="utf-8")