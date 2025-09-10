import numpy as np
import pandas as pd
import glob

# Lista todos os arquivos CSV na pasta 2025-08-01
csv_files = glob.glob(r'dataframe\*\*.csv')

# Lê todos os arquivos e concatena em um único DataFrame
dfs = []
for f in csv_files:
    try:
        df_temp = pd.read_csv(f)
        if 'entity_id' in df_temp.columns and 'attributes' in df_temp.columns:
            print(f"Arquivo válido: {f}")  # <-- Adicione esta linha
            dfs.append(df_temp)
    except Exception as e:
        print(f"Erro ao ler {f}: {e}")

if dfs:
    df = pd.concat(dfs, ignore_index=True)
else:
    print("Nenhum arquivo válido encontrado.")
    exit()

df_noduplicates = df.drop_duplicates(subset=['entity_id'])

print(len(df))
print(len(df_noduplicates))

df_onlyentity = pd.DataFrame(df['entity_id'].unique())
df_onlyentity.to_csv('tudoApenasEntidades.csv', index=False)
df_noduplicates.to_csv('tudoSemDuplicadas.csv', index=False)

df_teste = df_noduplicates[['entity_id', 'attributes']]