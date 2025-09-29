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
                    'timestamp': dt,
                    'date': dt.date(),
                    'hour': dt.hour
                })
            except:
                continue

# Primeira data disponível
primeira_data = min(d['date'] for d in dados)
print(f"Analisando dados da data: {primeira_data}")

# Filtrar por data
dados_data = [d for d in dados if d['date'] == primeira_data]

# Top 10 sensores por frequência
sensor_count = Counter(d['entity_id'] for d in dados_data)
principais_sensores = sensor_count.most_common(10)

print(f"\nPrincipais sensores na data {primeira_data}:")
for sensor, count in principais_sensores:
    print(f"{sensor}: {count}")

# Criar matriz de frequência
matriz = {}
for sensor, _ in principais_sensores:
    matriz[sensor] = {h: 0 for h in range(24)}
    sensor_data = [d for d in dados_data if d['entity_id'] == sensor]
    hora_count = Counter(d['hour'] for d in sensor_data)
    for hora, freq in hora_count.items():
        matriz[sensor][hora] = freq

# Gerar HTML com mapa de calor
html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mapa de Frequência por Horário - {primeira_data}</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .heatmap {{ display: grid; grid-template-columns: 200px repeat(24, 30px); gap: 2px; margin: 20px 0; }}
        .sensor-label {{ font-size: 12px; font-weight: bold; padding: 5px; text-align: right; display: flex; align-items: center; justify-content: end; }}
        .hour-header {{ text-align: center; font-size: 10px; font-weight: bold; }}
        .cell {{ width: 30px; height: 30px; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: bold; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Mapa de Frequência por Horário</h1>
        <h2>📅 {primeira_data}</h2>
        
        <div class="heatmap">
            <div></div>"""

# Headers das horas
for h in range(24):
    html += f'<div class="hour-header">{h:02d}</div>'

# Dados do mapa
for sensor, _ in principais_sensores:
    # Simplificar nome do sensor
    nome_simples = sensor.replace('automation.', '').replace('sensor.', '').replace('binary_sensor.', '').replace('_', ' ')[:25]
    html += f'<div class="sensor-label">{nome_simples}</div>'
    
    max_freq = max(matriz[sensor].values()) if max(matriz[sensor].values()) > 0 else 1
    for h in range(24):
        freq = matriz[sensor][h]
        if freq == 0:
            color = '#eee'
            opacity = 0.3
        else:
            intensity = freq / max_freq
            if intensity > 0.7:
                color = '#d32f2f'  # Vermelho
            elif intensity > 0.4:
                color = '#f57c00'  # Laranja
            elif intensity > 0.2:
                color = '#fbc02d'  # Amarelo
            else:
                color = '#388e3c'  # Verde
            opacity = 0.7 + (intensity * 0.3)
        
        html += f'<div class="cell" style="background-color: {color}; opacity: {opacity}">{freq if freq > 0 else ""}</div>'

html += """</div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📈 Estatísticas Gerais</h3>"""

# Estatísticas
total_eventos = len(dados_data)
sensores_unicos = len(set(d['entity_id'] for d in dados_data))
hora_count = Counter(d['hour'] for d in dados_data)
hora_pico = hora_count.most_common(1)[0] if hora_count else (0, 0)
sensor_mais_ativo = principais_sensores[0] if principais_sensores else ('N/A', 0)

html += f"""<p><strong>Total de eventos:</strong> {total_eventos}</p>
                <p><strong>Sensores únicos:</strong> {sensores_unicos}</p>
                <p><strong>Horário pico:</strong> {hora_pico[0]:02d}:00 ({hora_pico[1]} eventos)</p>
                <p><strong>Sensor mais ativo:</strong> {sensor_mais_ativo[0][:30]} ({sensor_mais_ativo[1]} eventos)</p>
            </div>
            
            <div class="stat-card">
                <h3>🕐 Distribuição por Período</h3>"""

# Análise por período
periodos = {
    'Madrugada (0-6h)': sum(1 for d in dados_data if 0 <= d['hour'] < 6),
    'Manhã (6-12h)': sum(1 for d in dados_data if 6 <= d['hour'] < 12),
    'Tarde (12-18h)': sum(1 for d in dados_data if 12 <= d['hour'] < 18),
    'Noite (18-24h)': sum(1 for d in dados_data if 18 <= d['hour'] < 24)
}

for periodo, count in periodos.items():
    percentual = (count / total_eventos * 100) if total_eventos > 0 else 0
    html += f'<p><strong>{periodo}:</strong> {count} eventos ({percentual:.1f}%)</p>'

html += """</div>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
            <p>🔴 Vermelho: Alta atividade | 🟠 Laranja: Média-alta | 🟡 Amarelo: Média-baixa | 🟢 Verde: Baixa</p>
        </div>
    </div>
</body>
</html>"""

with open('mapa_horario_frequencia.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nEstatísticas da data {primeira_data}:")
print(f"Total de eventos: {total_eventos}")
print(f"Número de sensores únicos: {sensores_unicos}")
print(f"Horário com mais atividade: {hora_pico[0]:02d}:00")
print(f"Sensor mais ativo: {sensor_mais_ativo[0]} ({sensor_mais_ativo[1]} eventos)")

print(f"\nDistribuição por período do dia:")
for periodo, count in periodos.items():
    percentual = (count / total_eventos * 100) if total_eventos > 0 else 0
    print(f"{periodo}: {count} eventos ({percentual:.1f}%)")

print(f"\nMapa HTML gerado: mapa_horario_frequencia.html")