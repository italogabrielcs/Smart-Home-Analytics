import csv
from datetime import datetime
from collections import Counter
import json

# Carregar dados
dados = []
with open('data/compilado_dados.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['timestamp'] and ('presenca' in row['entity_id'] or 'occupancy' in row['entity_id']):
            try:
                dt = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                dados.append({
                    'entity_id': row['entity_id'],
                    'hour': dt.hour,
                    'date': dt.date(),
                    'weekday': dt.strftime('%A'),
                    'new_state': row.get('new_state', ''),
                    'friendly_name': json.loads(row['attributes']).get('friendly_name', '').lower() if row['attributes'] else ''
                })
            except:
                continue

data_unica = dados[0]['date']
weekday = dados[0]['weekday']
dados_data = [d for d in dados if d['date'] == data_unica and d['new_state'] == 'on']

# Mapear locais
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

# Gerar HTML
html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mapa de Presença - {weekday}, {data_unica}</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
        .weekday {{ background: #4CAF50; color: white; padding: 10px; border-radius: 25px; display: inline-block; margin-bottom: 20px; }}
        .heatmap {{ display: grid; grid-template-columns: 100px repeat(24, 30px); gap: 2px; margin: 20px 0; }}
        .hour-header {{ text-align: center; font-size: 10px; font-weight: bold; }}
        .local-label {{ font-weight: bold; padding: 5px; text-align: right; }}
        .cell {{ width: 30px; height: 30px; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; }}
        .charts {{ display: flex; gap: 30px; margin-top: 30px; }}
        .chart {{ flex: 1; }}
        .bar {{ height: 20px; margin: 5px 0; border-radius: 10px; display: flex; align-items: center; padding-left: 10px; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 Mapa de Presença Smart Home</h1>
        <div class="weekday">📅 {weekday}, {data_unica}</div>
        
        <h2>🔥 Mapa de Calor por Horário</h2>
        <div class="heatmap">
            <div></div>"""

# Headers das horas
for h in range(24):
    html += f'<div class="hour-header">{h:02d}</div>'

# Dados do mapa de calor
cores = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
for i, local in enumerate(['Quarto', 'Sala', 'Cozinha', 'Banheiro']):
    html += f'<div class="local-label">{local}</div>'
    if local in locais_map:
        freq_hora = Counter(d['hour'] for d in locais_map[local])
        max_freq = max(freq_hora.values()) if freq_hora else 1
        for h in range(24):
            freq = freq_hora.get(h, 0)
            opacity = freq / max_freq if max_freq > 0 else 0
            color = cores[i]
            html += f'<div class="cell" style="background-color: {color}; opacity: {opacity + 0.1}">{freq if freq > 0 else ""}</div>'
    else:
        for h in range(24):
            html += '<div class="cell" style="background-color: #eee"></div>'

html += """</div>
        
        <div class="charts">
            <div class="chart">
                <h3>📊 Detecções por Local</h3>"""

# Gráfico por local
total = len(dados_data)
for i, local in enumerate(['Quarto', 'Sala', 'Cozinha', 'Banheiro']):
    count = len(locais_map.get(local, []))
    width = (count / total * 100) if total > 0 else 0
    html += f'<div class="bar" style="background-color: {cores[i]}; width: {width}%">{local}: {count}</div>'

html += """</div>
            
            <div class="chart">
                <h3>⏰ Atividade por Horário</h3>"""

# Gráfico por horário
freq_total = Counter(d['hour'] for d in dados_data)
max_total = max(freq_total.values()) if freq_total else 1
for h in range(24):
    freq = freq_total.get(h, 0)
    width = (freq / max_total * 100) if max_total > 0 else 0
    color = '#FF6B6B' if freq > max_total * 0.7 else '#4ECDC4' if freq > max_total * 0.3 else '#95E1D3'
    html += f'<div class="bar" style="background-color: {color}; width: {width}%">{h:02d}:00 - {freq}</div>'

html += """</div>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>📈 Total de detecções: <strong>{}</strong> | 🕐 Horário pico: <strong>{}:00</strong></p>
        </div>
    </div>
</body>
</html>""".format(total, max(freq_total, key=freq_total.get) if freq_total else 0)

with open('mapa_presenca.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Gráfico HTML gerado: mapa_presenca.html")
print(f"Data: {weekday}, {data_unica}")
print(f"Total detecções: {total}")