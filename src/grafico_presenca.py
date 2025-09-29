import csv
from datetime import datetime
from collections import Counter
import json

# Carregar dados
dados = []
with open('./data/compilado_dados.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['timestamp'] and ('presenca' in row['entity_id'] or 'occupancy' in row['entity_id']):
            try:
                dt = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                
                # Extrair friendly_name do JSON
                friendly_name = ''
                if row['attributes']:
                    try:
                        attrs = json.loads(row['attributes'])
                        friendly_name = attrs.get('friendly_name', '').lower()
                    except:
                        pass
                
                dados.append({
                    'entity_id': row['entity_id'],
                    'hour': dt.hour,
                    'date': dt.date(),
                    'new_state': row.get('new_state', ''),
                    'friendly_name': friendly_name
                })
            except:
                continue

# Usar única data disponível
data_unica = dados[0]['date']
dados_data = [d for d in dados if d['date'] == data_unica and d['new_state'] == 'on']

# Mapear por friendly_name
locais_map = {}
for d in dados_data:
    if 'quarto' in d['friendly_name']:
        locais_map['Quarto'] = locais_map.get('Quarto', []) + [d]
    elif 'sala' in d['friendly_name']:
        locais_map['Sala'] = locais_map.get('Sala', []) + [d]
    elif 'cozinha' in d['friendly_name']:
        locais_map['Cozinha'] = locais_map.get('Cozinha', []) + [d]
    elif 'banheiro' in d['friendly_name']:
        locais_map['Banheiro'] = locais_map.get('Banheiro', []) + [d]

# Gráfico de barras ASCII
print(f"\nGRÁFICO DE PRESENÇA POR HORÁRIO - {data_unica}")
print("="*60)

freq_total = Counter(d['hour'] for d in dados_data)
max_freq = max(freq_total.values()) if freq_total else 1

for h in range(24):
    freq = freq_total.get(h, 0)
    barra = "█" * int((freq / max_freq) * 30)
    print(f"{h:02d}:00 |{barra:<30}| {freq}")

print("\nGRÁFICO POR LOCAL")
print("="*40)

for local in ['Quarto', 'Sala', 'Cozinha', 'Banheiro']:
    if local in locais_map:
        count = len(locais_map[local])
        barra = "█" * int((count / len(dados_data)) * 20)
        print(f"{local:<8} |{barra:<20}| {count}")
    else:
        print(f"{local:<8} |{'':20}| 0")

# Mapa de calor ASCII
print(f"\nMAPA DE CALOR - {data_unica}")
print("="*80)
print("Local".ljust(12), end="")
for h in range(0, 24, 2):
    print(f"{h:2d}".rjust(4), end="")
print()
print("-"*80)

for local in ['Quarto', 'Sala', 'Cozinha', 'Banheiro']:
    print(local.ljust(12), end="")
    if local in locais_map:
        freq_hora = Counter(d['hour'] for d in locais_map[local])
        max_local = max(freq_hora.values()) if freq_hora else 1
        for h in range(0, 24, 2):
            freq = freq_hora.get(h, 0)
            if freq == 0:
                symbol = " . "
            elif freq <= max_local * 0.3:
                symbol = " ░ "
            elif freq <= max_local * 0.6:
                symbol = " ▒ "
            else:
                symbol = " █ "
            print(symbol, end="")
    else:
        for h in range(0, 24, 2):
            print(" . ", end="")
    print()

print("="*80)
print("Legenda: . = sem detecção, ░ = baixa, ▒ = média, █ = alta")