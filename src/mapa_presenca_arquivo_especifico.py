import csv
from datetime import datetime
from collections import Counter

# Analisar arquivo específico (horário diferente do dia)
arquivo = '../data/2025-08-17/07.csv'  # Dados das 7h

dados = []
with open(arquivo, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['timestamp'] and 'presenca' in row['entity_id'] and row['new_state'] == 'on':
            try:
                dt = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                dados.append({
                    'entity_id': row['entity_id'],
                    'hour': dt.hour,
                    'minute': dt.minute
                })
            except:
                continue

print(f"MAPA DE PRESENÇA - ARQUIVO {arquivo.split('/')[-1]} (Dados Reais)")
print("="*80)

if len(dados) == 0:
    print("Nenhum sensor de presença ativo neste período")
else:
    locais = {
        'binary_sensor.presenca_quarto_motion': 'Quarto',
        'binary_sensor.presenca_sala_motion': 'Sala',
        'binary_sensor.presenca_cozinha_motion': 'Cozinha', 
        'binary_sensor.presenca_banheiro_motion': 'Banheiro'
    }
    
    print("Detecções encontradas:")
    for dado in dados:
        local = locais.get(dado['entity_id'], dado['entity_id'])
        print(f"{local}: {dado['hour']:02d}:{dado['minute']:02d}")

print("="*80)