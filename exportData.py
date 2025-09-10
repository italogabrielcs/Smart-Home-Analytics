import numpy as np

import pandas as pd

df = pd.read_csv('23.csv', '/2025-08-01/00.csv')

df_noduplicates = df.drop_duplicates(subset=['entity_id'])

print(len(df))
print(len(df_noduplicates))
#entity_id
df_onlyentity = pd.DataFrame(df['entity_id'].unique())
df_onlyentity.to_csv('23apenasentidades.csv')
df_noduplicates.to_csv('23semduplicatas.csv')

df_teste = df_noduplicates[['entity_id', 'attributes']]

df_teste.to_csv('23teste.csv', index=False)