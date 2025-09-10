# pegar dados csv 
# juntar dados csv 
# salvar dados (salvar sem duplicata, salvar completo, salvar uma parte)

import glob
import pandas as pd
import os

class Join: 
    # TODO: colocar o tipo de arquivo que sera lido e salvo:
    def __init__(self, caminho_dados:str):
        self.caminho_dados = caminho_dados
    
    def join_csv(self) -> pd.DataFrame: 
        # TODO: colocar um tratamento
        joinDadosCsv = glob.glob(os.path.join(self.caminho_dados,"**/*.csv"),recursive=True)

        # TODO: colocar tratamento aqui:
        lista_df = []
        for arquivo in joinDadosCsv:
            try:
                df = pd.read_csv(arquivo, on_bad_lines="warn")
                lista_df.append(df)
            except Exception as e:
                print(f"Erro ao ler {arquivo} -> {e}")
        
        return pd.concat(lista_df,ignore_index=True)

    def save_df_csv(self, sem_duplicata:bool = False, completo:bool = True, salvar_atributo:str = None):

        dados_csv = self.join_csv(self.caminho_dados)
        caminho_salvar = "data"

        if not os.path.exists(caminho_salvar):
            raise FileNotFoundError(f"Diretorio não encontrado: {caminho_salvar}")

        if self.completo:
            try:
                dados_csv.to_csv("../data/join_data_sensor.csv",index=False)
            except Exception as e: 
                print(f"")



        
