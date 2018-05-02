import pandas as pd

df = pd.read_csv('data_maxentropy.csv')
df.head()

col = ['class', 'sentence']
df = df[col]
df = df[pd.notnull(df['sentence'])]

df.columns = ['class', 'sentence']

df['category_id'] = df['class'].factorize()[0]
category_id_df = df[['class', 'category_id']].drop_duplicates().sort_values('category_id')
category_to_id = dict(category_id_df.values)
id_to_category = dict(category_id_df[['category_id', 'class']].values)
print(df.head())