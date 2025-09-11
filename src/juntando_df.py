import glob
import pandas as pd
import os

class JuntarArquivoCsv:
 
    def __init__(self, caminho_dados:str):
        self.caminho_dados = caminho_dados
    
    def juntar_csv(self) -> pd.DataFrame: 
        juntar_dados_csv = glob.glob(os.path.join(self.caminho_dados,"**/*.csv"),recursive=True)

        lista_df = []
        for arquivo in juntar_dados_csv:
            try:
                df = pd.read_csv(arquivo, on_bad_lines="warn")
                lista_df.append(df)
            except Exception as e:
                print(f"Erro ao ler {arquivo} -> {e}")
        
        if lista_df: 
            return pd.concat(lista_df,ignore_index=True)
        else: 
            raise ValueError("lista concatenada de dados CSV vazia")

    def salvar_df_csv(self, sem_duplicata_sensor:bool = False, completo:bool = True, salvar_atributo:str = None):

        dados_csv = self.juntar_csv()
        
        caminho_salvar = {
            "arquivo_completo" : "../data/compilado_dados.csv",
            "arquivo_sem_duplicata_sensor" : "../data/compilado_dados_sem_duplicata_sensor.csv",
            "arquivo_atributo_especifico" : "../data/compilado_atributo_especifico.csv",

            }

        diretorio = os.path.dirname(caminho_salvar["arquivo_completo"])
        if not os.path.exists(diretorio):
            raise FileNotFoundError(f"Diretorio não encontrado: {diretorio}")

        if completo:
            try:
                dados_csv.to_csv(caminho_salvar["arquivo_completo"],index=False)
            except Exception as e: 
                print(f"Erro ao salvar o arquivo CSV: {e}")

        if sem_duplicata_sensor:
            try:
                dados_csv_sem_duplicata_sensor = dados_csv.drop_duplicates(subset=["entity_id"])
                dados_csv_sem_duplicata_sensor.to_csv(caminho_salvar["arquivo_sem_duplicata_sensor"], index=False)
            except Exception as e:
                print(f"Erro ao salvar o arquivo CSV: {e}")

        if salvar_atributo != None:
            if salvar_atributo in dados_csv.columns: 
                dados_csv[salvar_atributo].to_csv(caminho_salvar["arquivo_atributo_especifico"], index=False)
            else: 
                print(f"Coluna do data frame atribuido não existe nesse data frame")



        
