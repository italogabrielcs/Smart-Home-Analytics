#!/usr/bin/env python3
"""
Análise simples de presença usando apenas bibliotecas padrão do Python
"""

import csv
import json
from datetime import datetime
from collections import defaultdict, Counter

def carregar_dados(arquivo_csv):
    """Carrega dados do CSV"""
    dados = []
    with open(arquivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dados.append(row)
    return dados

def filtrar_sensores_presenca(dados):
    """Filtra apenas sensores de presença dos principais locais"""
    sensores_presenca = []
    locais_principais = ['sala', 'quarto', 'banheiro', 'cozinha']
    
    for row in dados:
        entity_id = row['entity_id']
        if 'presenca' in entity_id and 'motion' in entity_id:
            try:
                # Parse do JSON attributes
                attributes = json.loads(row['attributes'])
                friendly_name = attributes.get('friendly_name', '').lower()
                
                # Verificar se é um dos locais principais
                for local in locais_principais:
                    if local in friendly_name:
                        # Parse do timestamp
                        timestamp_str = row['timestamp']
                        if timestamp_str:
                            dt = datetime.fromisoformat(timestamp_str.replace('T', ' ').replace('Z', ''))
                            
                            sensores_presenca.append({
                                'entity_id': entity_id,
                                'friendly_name': local,
                                'old_state': row['old_state'],
                                'new_state': row['new_state'],
                                'timestamp': dt,
                                'data': dt.date(),
                                'hora': dt.hour,
                                'dia_semana': dt.strftime('%A')
                            })
                        break
            except (json.JSONDecodeError, ValueError):
                continue
    
    return sensores_presenca

def analisar_presenca(dados_presenca):
    """Análise básica dos dados de presença"""
    # Filtrar apenas ativações (new_state = 'on')
    ativacoes = [d for d in dados_presenca if d['new_state'] == 'on']
    
    print("=== ANÁLISE DE PRESENÇA NOS 4 PRINCIPAIS LOCAIS ===\n")
    
    # Estatísticas gerais
    if ativacoes:
        datas = [d['data'] for d in ativacoes]
        data_min = min(datas)
        data_max = max(datas)
        print(f"Período analisado: {data_min} a {data_max}")
        print(f"Total de ativações: {len(ativacoes)}")
        print(f"Dias únicos: {len(set(datas))}\n")
    
    # Ativações por local
    print("--- ATIVAÇÕES POR LOCAL ---")
    locais_count = Counter(d['friendly_name'] for d in ativacoes)
    for local, count in locais_count.most_common():
        print(f"{local.capitalize()}: {count} ativações")
    
    # Padrão por hora do dia
    print("\n--- PADRÃO POR HORA DO DIA ---")
    for local in ['sala', 'quarto', 'banheiro', 'cozinha']:
        local_data = [d for d in ativacoes if d['friendly_name'] == local]
        if local_data:
            horas_count = Counter(d['hora'] for d in local_data)
            hora_pico = max(horas_count.items(), key=lambda x: x[1])
            print(f"{local.capitalize()}: Pico às {hora_pico[0]}h ({hora_pico[1]} ativações)")
    
    # Padrão por dia da semana
    print("\n--- PADRÃO POR DIA DA SEMANA ---")
    dias_count = defaultdict(lambda: defaultdict(int))
    for d in ativacoes:
        dias_count[d['friendly_name']][d['dia_semana']] += 1
    
    for local in ['sala', 'quarto', 'banheiro', 'cozinha']:
        if local in dias_count:
            print(f"\n{local.capitalize()}:")
            for dia, count in sorted(dias_count[local].items()):
                print(f"  {dia}: {count} ativações")
    
    # Distribuição por hora (resumida)
    print("\n--- DISTRIBUIÇÃO POR HORA (TODAS AS LOCALIZAÇÕES) ---")
    todas_horas = Counter(d['hora'] for d in ativacoes)
    for hora in sorted(todas_horas.keys()):
        count = todas_horas[hora]
        barra = '█' * (count // 10) if count > 0 else ''
        print(f"{hora:2d}h: {count:4d} {barra}")

def main():
    """Função principal"""
    try:
        # Carregar dados
        print("Carregando dados...")
        dados = carregar_dados('../data/compilado_dados.csv')
        print(f"Total de registros carregados: {len(dados)}")
        
        # Filtrar sensores de presença
        print("Filtrando sensores de presença...")
        dados_presenca = filtrar_sensores_presenca(dados)
        print(f"Registros de presença encontrados: {len(dados_presenca)}")
        
        if dados_presenca:
            # Realizar análise
            analisar_presenca(dados_presenca)
        else:
            print("Nenhum dado de presença encontrado!")
            
    except FileNotFoundError:
        print("Erro: Arquivo '../data/compilado_dados.csv' não encontrado!")
    except Exception as e:
        print(f"Erro durante a análise: {e}")

if __name__ == "__main__":
    main()