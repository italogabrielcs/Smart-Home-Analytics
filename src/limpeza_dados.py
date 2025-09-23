import pandas as pd
import re
import numpy as np
import json 

# TODO : 
# Melhorar nome desses metodos
# melhorar nome de variaveis
# deixar em ordem de execução
# formatar espaços para deixar legivel
# colocar tratamento de exeções 

class LimpezaDados:

    def __init__(self, atributo_filtrar:str, data_frame:pd.DataFrame):
        self.atributo_filtrar = atributo_filtrar
        self.data_frame = data_frame
        self.arrumando_data()

    def get_dados_sem_duplicata(self) -> pd.DataFrame:
        return self.data_frame.drop_duplicates(subset=self.atributo_filtrar)

    # TODO: mudar nome funcao: 
    def get_dados_filtro(self, atributos_filtrados: pd.DataFrame) -> pd.DataFrame:
        valores_filtro = atributos_filtrados[self.atributo_filtrar].unique()
        df_filtrado = self.data_frame[self.data_frame[self.atributo_filtrar].isin(valores_filtro)]
        return df_filtrado.reset_index(drop=True)

    # TODO: ver se essa função faz sentido
    def filtrar(self, filtro:str) -> pd.DataFrame:

        dados_sem_suplicata = self.get_dados_sem_duplicata()
        dados_sem_suplicata = dados_sem_suplicata[dados_sem_suplicata[self.atributo_filtrar].str.contains(filtro, case=False)]
        return dados_sem_suplicata[[self.atributo_filtrar]].reset_index(drop=True)
    
    def data_frame_dados_filtrados(self, filtro:str) -> pd.DataFrame:
        atributos_filtrados = self.filtrar(filtro)
        return self.get_dados_filtro(atributos_filtrados)

    def arrumando_data(self, atributo_data:str='timestamp') -> pd.DataFrame:
        self.data_frame[atributo_data] = pd.to_datetime(self.data_frame[atributo_data], errors='coerce').dt.floor('min')
        self.data_frame['date'] = self.data_frame[atributo_data].dt.strftime('%d/%m/%Y')
        self.data_frame['hora'] = self.data_frame[atributo_data].dt.strftime('%H:%M') 
        self.data_frame.drop(columns=atributo_data, inplace=True)

    def tratando_json_sensor_presenca(self, atributo_json:str, data_frame_atributo:pd.DataFrame, data_frame_json:bool = False) -> pd.DataFrame:
        lista_dic = []

        for elemento in data_frame_atributo[atributo_json]:
            try:
                registro = json.loads(elemento)
                lista_dic.append(registro)
            except json.JSONDecodeError:
                lista_dic.append(None)

        if data_frame_json:
            return self.juntar_json_data_frame(lista_dic, atributo_json, data_frame_atributo)

        return pd.DataFrame(lista_dic)

    def juntar_json_data_frame(self, atributos_juntar:list, atributo_json:str, data_frame_juntar:pd.DataFrame) -> pd.DataFrame:
        lista_atributos_remover = ["min", "max", "step", "mode", "restored", "supported_features"] 
        df = pd.DataFrame(atributos_juntar)
        df.drop(columns=lista_atributos_remover, inplace=True)
        df = pd.concat([data_frame_juntar, df], axis=1)
        df.drop(columns=atributo_json, inplace=True)
        return df
    
    def classificando_feriado(self, data_feriados:str = "timestamp") -> pd.DataFrame:
        pass 
    
    def filtrar_local_casa(self, data_frame:pd.DataFrame) -> pd.DataFrame:

        lista_locais_casa = ['sala', 'quarto', 'cozinha', 'banheiro']

        padrao = re.compile(r'\b(' + '|'.join(lista_locais_casa) + ')\b', flags=re.IGNORECASE)

        for val in data_frame['friendly_name'].items():
             pass 