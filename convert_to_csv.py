import json
import pandas as pd


with open("output.json", "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)
df.to_csv("data.csv", index=False, encoding="utf-8")

print(df.head())