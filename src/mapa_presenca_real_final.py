import csv
from datetime import datetime
from collections import Counter
import json
import matplotlib.pyplot as plt
import numpy as np

# Carregar dados
dados = []
with open('data/compilado_dados.csv', 'r', encoding='utf-8') as f:
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

print(f"MAPA DE PRESENÇA - {data_unica} (Dados Reais)")
print("="*80)
print("Local".ljust(20), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()
print("-"*80)

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

# Exibir mapa
for local in ['Quarto', 'Sala', 'Cozinha', 'Banheiro']:
    print(local.ljust(20), end="")
    if local in locais_map:
        freq_hora = Counter(d['hour'] for d in locais_map[local])
        for h in range(24):
            freq = freq_hora.get(h, 0)
            print(f"{freq:3d}" if freq > 0 else "  .", end="")
    else:
        for h in range(24):
            print("  .", end="")
    print()

print("="*80)
total = len(dados_data)
print(f"Total detecções: {total}")

if total > 0:
    hora_pico = Counter(d['hour'] for d in dados_data).most_common(1)[0]
    print(f"Horário pico: {hora_pico[0]:02d}:00 ({hora_pico[1]} detecções)")
    
    for local in ['Quarto', 'Sala', 'Cozinha', 'Banheiro']:
        if local in locais_map:
            count = len(locais_map[local])
            print(f"{local}: {count} detecções")

# Gerar gráfico
locais = ['Quarto', 'Sala', 'Cozinha', 'Banheiro']
horas = list(range(24))
matriz = np.zeros((len(locais), 24))

for i, local in enumerate(locais):
    if local in locais_map:
        freq_hora = Counter(d['hour'] for d in locais_map[local])
        for h in range(24):
            matriz[i, h] = freq_hora.get(h, 0)

plt.figure(figsize=(12, 6))
plt.imshow(matriz, cmap='YlOrRd', aspect='auto')
plt.colorbar(label='Detecções')
plt.yticks(range(len(locais)), locais)
plt.xticks(range(0, 24, 2), [f'{h:02d}:00' for h in range(0, 24, 2)])
plt.xlabel('Horário')
plt.ylabel('Local')
plt.title(f'Mapa de Presença - {data_unica}')

for i in range(len(locais)):
    for j in range(24):
        if matriz[i, j] > 0:
            plt.text(j, i, int(matriz[i, j]), ha='center', va='center', color='black', fontsize=8)

plt.tight_layout()
plt.savefig('mapa_presenca.png', dpi=300, bbox_inches='tight')
plt.show()