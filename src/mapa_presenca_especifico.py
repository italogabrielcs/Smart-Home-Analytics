import csv
from datetime import datetime
from collections import Counter

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

# Filtrar apenas sensores de presença específicos
sensores_presenca = [
    'binary_sensor.presenca_quarto_motion',
    'binary_sensor.presenca_sala_motion', 
    'binary_sensor.presenca_cozinha_motion',
    'binary_sensor.presenca_banheiro_motion'
]

# Usar primeira data
data_unica = dados[0]['date']
dados_presenca = [d for d in dados if d['date'] == data_unica and d['entity_id'] in sensores_presenca and d['new_state'] == 'on']

print(f"MAPA DE PRESENÇA - {data_unica}")
print("="*80)
print("Local".ljust(20), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()
print("-"*80)

# Mapear sensores para locais
locais = {
    'binary_sensor.presenca_quarto_motion': 'Quarto',
    'binary_sensor.presenca_sala_motion': 'Sala',
    'binary_sensor.presenca_cozinha_motion': 'Cozinha', 
    'binary_sensor.presenca_banheiro_motion': 'Banheiro'
}

for sensor in sensores_presenca:
    local = locais[sensor]
    print(local.ljust(20), end="")
    
    freq_hora = Counter(d['hour'] for d in dados_presenca if d['entity_id'] == sensor)
    
    for h in range(24):
        freq = freq_hora.get(h, 0)
        print(f"{freq:3d}" if freq > 0 else "  .", end="")
    print()

print("="*80)
print("Legenda: '.' = sem detecção, números = ativações de presença")