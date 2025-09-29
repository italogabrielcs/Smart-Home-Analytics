import csv
from datetime import datetime
from collections import Counter
import json
import base64
import io

# Carregar dados
dados = []
with open('../data/compilado_dados.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['timestamp'] and ('presenca' in row['entity_id'] or 'occupancy' in row['entity_id']):
            try:
                dt = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                dados.append({
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

# Gerar gráfico como string base64 (simulado)
def create_chart_data():
    locais = ['Quarto', 'Sala', 'Cozinha', 'Banheiro']
    matriz = []
    for local in locais:
        linha = []
        if local in locais_map:
            freq_hora = Counter(d['hour'] for d in locais_map[local])
            for h in range(24):
                linha.append(freq_hora.get(h, 0))
        else:
            linha = [0] * 24
        matriz.append(linha)
    return matriz

matriz = create_chart_data()

# HTML com matplotlib simulado
html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Análise de Presença - {weekday}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(45deg, #1e3c72, #2a5298); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: rgba(255,255,255,0.95); padding: 30px; border-radius: 20px; margin-bottom: 20px; text-align: center; }}
        .weekday-badge {{ background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; padding: 15px 30px; border-radius: 50px; font-size: 24px; font-weight: bold; display: inline-block; }}
        .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .chart-card {{ background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
        .heatmap {{ display: grid; grid-template-columns: 80px repeat(24, 1fr); gap: 3px; margin: 20px 0; }}
        .cell {{ aspect-ratio: 1; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; }}
        .hour-label {{ font-size: 10px; text-align: center; font-weight: bold; }}
        .local-label {{ font-weight: bold; display: flex; align-items: center; justify-content: end; padding-right: 10px; }}
        .stats {{ display: flex; justify-content: space-around; margin-top: 20px; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #2a5298; }}
        .stat-label {{ color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0 0 20px 0; color: #333;">🏠 Smart Home Analytics</h1>
            <div class="weekday-badge">📅 {weekday}, {data_unica}</div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h2 style="color: #333; margin-top: 0;">🔥 Mapa de Calor - Presença por Horário</h2>
                <div class="heatmap">
                    <div></div>"""

# Headers das horas
for h in range(24):
    html += f'<div class="hour-label">{h}</div>'

# Cores para cada local
cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
locais = ['Quarto', 'Sala', 'Cozinha', 'Banheiro']

for i, local in enumerate(locais):
    html += f'<div class="local-label">{local}</div>'
    for h in range(24):
        valor = matriz[i][h]
        max_local = max(matriz[i]) if max(matriz[i]) > 0 else 1
        intensidade = valor / max_local if max_local > 0 else 0
        opacity = 0.2 + (intensidade * 0.8)
        html += f'<div class="cell" style="background-color: {cores[i]}; opacity: {opacity}; color: white;">{valor if valor > 0 else ""}</div>'

html += """</div>
            </div>
            
            <div class="chart-card">
                <h2 style="color: #333; margin-top: 0;">📊 Distribuição por Local</h2>"""

# Gráfico de barras por local
total = len(dados_data)
for i, local in enumerate(locais):
    count = len(locais_map.get(local, []))
    percentage = (count / total * 100) if total > 0 else 0
    html += f"""<div style="margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="font-weight: bold;">{local}</span>
                        <span>{count} ({percentage:.1f}%)</span>
                    </div>
                    <div style="background: #eee; border-radius: 10px; height: 20px;">
                        <div style="background: {cores[i]}; height: 100%; width: {percentage}%; border-radius: 10px;"></div>
                    </div>
                </div>"""

html += """</div>
        </div>
        
        <div class="chart-card" style="margin-top: 20px;">
            <h2 style="color: #333; margin-top: 0;">⏰ Atividade ao Longo do Dia</h2>
            <div style="display: flex; align-items: end; height: 200px; gap: 2px; padding: 20px 0;">"""

# Gráfico de barras por horário
freq_total = Counter(d['hour'] for d in dados_data)
max_freq = max(freq_total.values()) if freq_total else 1

for h in range(24):
    freq = freq_total.get(h, 0)
    height = (freq / max_freq * 180) if max_freq > 0 else 0
    color = '#FF6B6B' if freq > max_freq * 0.7 else '#4ECDC4' if freq > max_freq * 0.4 else '#96CEB4'
    html += f"""<div style="flex: 1; display: flex; flex-direction: column; align-items: center;">
                    <div style="font-size: 10px; margin-bottom: 5px;">{freq if freq > 0 else ''}</div>
                    <div style="background: {color}; width: 100%; height: {height}px; border-radius: 3px 3px 0 0;"></div>
                    <div style="font-size: 9px; margin-top: 5px; transform: rotate(-45deg);">{h:02d}</div>
                </div>"""

html += """</div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{}</div>
                <div class="stat-label">Total Detecções</div>
            </div>
            <div class="stat">
                <div class="stat-value">{}:00</div>
                <div class="stat-label">Horário Pico</div>
            </div>
            <div class="stat">
                <div class="stat-value">{}</div>
                <div class="stat-label">Local Mais Ativo</div>
            </div>
        </div>
    </div>
</body>
</html>""".format(
    total,
    max(freq_total, key=freq_total.get) if freq_total else 0,
    max(locais_map, key=lambda x: len(locais_map[x])) if locais_map else 'N/A'
)

with open('dashboard_presenca.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard HTML gerado: dashboard_presenca.html")
print(f"Análise para {weekday}, {data_unica}")
print(f"Total de detecções: {total}")
if freq_total:
    print(f"Horário pico: {max(freq_total, key=freq_total.get)}:00")
if locais_map:
    print(f"Local mais ativo: {max(locais_map, key=lambda x: len(locais_map[x]))}")