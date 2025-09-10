import pandas as pd
import json
import numpy as np

# Nome do arquivo de entrada e saída
arquivo_entrada = 'todos.csv'
arquivo_saida = 'json_extraidos_sem_duplicados.csv'

try:
    # Carregar o arquivo CSV
    df = pd.read_csv(arquivo_entrada)

    # Verificar se a coluna 'attributes' existe
    if 'attributes' in df.columns:
        # Função para analisar o JSON em cada linha da coluna 'attributes'
        def parse_attributes(json_string):
            try:
                return json.loads(json_string)
            except (json.JSONDecodeError, TypeError):
                return None

        # Aplica a função de análise a cada item da coluna 'attributes'
        attributes_data = df['attributes'].apply(parse_attributes)

        # Remove as linhas onde a análise JSON falhou
        attributes_data = attributes_data.dropna()

        # Cria um novo DataFrame a partir dos dados JSON
        attributes_df = pd.json_normalize(attributes_data.tolist())

        # Converte todas as colunas para string para permitir drop_duplicates
        attributes_df = attributes_df.astype(str)

        # Guarda o número de linhas antes de remover os duplicados
        linhas_antes = len(attributes_df)

        # Remove duplicados
        attributes_df = attributes_df.drop_duplicates()

        # Guarda o número de linhas depois de remover os duplicados
        linhas_depois = len(attributes_df)
        
        # Calcula quantos duplicados foram removidos
        duplicados_removidos = linhas_antes - linhas_depois

        # Salva o DataFrame resultante (sem duplicados) em um novo arquivo CSV
        attributes_df.to_csv(arquivo_saida, index=False)

        print(f"Foram encontradas e removidas {duplicados_removidos} linhas duplicadas.")
        print(f"Dados extraídos com sucesso e salvos no arquivo: '{arquivo_saida}'")
        print("\nAmostra dos dados salvos (sem duplicados):")
        print(attributes_df.head())

    else:
        print(f"A coluna 'attributes' não foi encontrada no arquivo '{arquivo_entrada}'.")

except FileNotFoundError:
    print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")