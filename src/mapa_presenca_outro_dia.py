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

# Pegar todas as datas disponíveis
datas_disponiveis = list(set(d['date'] for d in dados))
datas_disponiveis.sort()

# Usar segunda data disponível (se existir)
if len(datas_disponiveis) > 1:
    data_escolhida = datas_disponiveis[1]
else:
    data_escolhida = datas_disponiveis[0]

dados_data = [d for d in dados if d['date'] == data_escolhida and d['entity_id'] in [
    'binary_sensor.presenca_quarto_motion',
    'binary_sensor.presenca_sala_motion', 
    'binary_sensor.presenca_cozinha_motion',
    'binary_sensor.presenca_banheiro_motion'
] and d['new_state'] == 'on']

print(f"MAPA DE PRESENÇA - {data_escolhida}")
print("="*80)
print("Local".ljust(20), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()
print("-"*80)

locais = {
    'binary_sensor.presenca_quarto_motion': 'Quarto',
    'binary_sensor.presenca_sala_motion': 'Sala',
    'binary_sensor.presenca_cozinha_motion': 'Cozinha', 
    'binary_sensor.presenca_banheiro_motion': 'Banheiro'
}

for sensor, local in locais.items():
    print(local.ljust(20), end="")
    freq_hora = Counter(d['hour'] for d in dados_data if d['entity_id'] == sensor)
    for h in range(24):
        freq = freq_hora.get(h, 0)
        print(f"{freq:3d}" if freq > 0 else "  .", end="")
    print()

print("="*80)
total_deteccoes = len(dados_data)
print(f"Total detecções: {total_deteccoes}")
print(f"Datas disponíveis: {len(datas_disponiveis)}")
if total_deteccoes > 0:
    hora_pico = Counter(d['hour'] for d in dados_data).most_common(1)[0]
    print(f"Horário pico: {hora_pico[0]:02d}:00 ({hora_pico[1]} detecções)")