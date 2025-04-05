import pandas as pd

dataframes = []
for i in range(1, 11):
    data_path = f""
    df = pd.read_csv(data_path)
    df = df[['translated_title', 'translated_summary', 'categories']]
    dataframes.append(df)


combined_df = pd.concat(dataframes, ignore_index=True)
output_file = "translated_data.csv"
combined_df.to_csv(output_file, index=False)