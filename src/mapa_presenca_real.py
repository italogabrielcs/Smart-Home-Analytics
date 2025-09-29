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
datas_disponiveis = sorted(set(d['date'] for d in dados))
print(f"Datas disponíveis: {datas_disponiveis}")

# Sensores de presença específicos
sensores_presenca = [
    'binary_sensor.presenca_quarto_motion',
    'binary_sensor.presenca_sala_motion', 
    'binary_sensor.presenca_cozinha_motion',
    'binary_sensor.presenca_banheiro_motion'
]

locais = {
    'binary_sensor.presenca_quarto_motion': 'Quarto',
    'binary_sensor.presenca_sala_motion': 'Sala',
    'binary_sensor.presenca_cozinha_motion': 'Cozinha', 
    'binary_sensor.presenca_banheiro_motion': 'Banheiro'
}

# Analisar cada data disponível
for data in datas_disponiveis:
    dados_data = [d for d in dados if d['date'] == data and d['entity_id'] in sensores_presenca and d['new_state'] == 'on']
    
    if len(dados_data) == 0:
        continue
        
    print(f"\nMAPA DE PRESENÇA - {data}")
    print("="*80)
    print("Local".ljust(20), end="")
    for h in range(24):
        print(f"{h:2d}".rjust(3), end="")
    print()
    print("-"*80)

    for sensor, local in locais.items():
        print(local.ljust(20), end="")
        freq_hora = Counter(d['hour'] for d in dados_data if d['entity_id'] == sensor)
        for h in range(24):
            freq = freq_hora.get(h, 0)
            print(f"{freq:3d}" if freq > 0 else "  .", end="")
        print()

    print("="*80)
    
    # Resumo
    total = len(dados_data)
    print(f"Total detecções: {total}")
    
    if total > 0:
        hora_pico = Counter(d['hour'] for d in dados_data).most_common(1)[0]
        print(f"Horário pico: {hora_pico[0]:02d}:00 ({hora_pico[1]} detecções)")
        
        # Por local
        for sensor, local in locais.items():
            count = len([d for d in dados_data if d['entity_id'] == sensor])
            if count > 0:
                print(f"{local}: {count} detecções")