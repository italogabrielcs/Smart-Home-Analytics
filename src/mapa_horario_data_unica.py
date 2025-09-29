import csv
from datetime import datetime
from collections import Counter
import json

# Carregar dados
dados = []
with open('../data/compilado_dados.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['timestamp']:
            try:
                dt = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                dados.append({
                    'entity_id': row['entity_id'],
                    'hour': dt.hour,
                    'date': dt.date(),
                    'new_state': row.get('new_state', '')
                })
            except:
                continue

# Usar apenas uma data
data_unica = dados[0]['date']
dados_data = [d for d in dados if d['date'] == data_unica]

# Principais sensores
sensores_freq = Counter(d['entity_id'] for d in dados_data)
top_sensores = sensores_freq.most_common(8)

print(f"MAPA DE HORÁRIO E FREQUÊNCIA - {data_unica}")
print("="*90)

# Cabeçalho
print("Sensor".ljust(35), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()
print("-"*90)

# Matriz de frequência
for sensor, total in top_sensores:
    nome = sensor.replace('automation.', '').replace('sensor.', '').replace('binary_sensor.', '')
    nome = nome.replace('_', ' ')[:30]
    
    print(nome.ljust(35), end="")
    
    # Contar por hora
    freq_hora = Counter(d['hour'] for d in dados_data if d['entity_id'] == sensor)
    
    for h in range(24):
        freq = freq_hora.get(h, 0)
        if freq == 0:
            print("  .", end="")
        else:
            print(f"{freq:3d}", end="")
    print()

print("="*90)
print(f"Total de eventos analisados: {len(dados_data)}")
print(f"Data: {data_unica}")
print("Legenda: '.' = sem atividade, números = quantidade de eventos")