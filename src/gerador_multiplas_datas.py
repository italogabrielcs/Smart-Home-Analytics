import csv
from datetime import datetime, timedelta
import json

# CONFIGURAÇÃO - ADICIONE AS DATAS QUE QUER ANALISAR
DATAS_PARA_ANALISAR = [
    "2025-08-17",
    "2025-08-18", 
    "2025-08-19"
]

def gerar_relatorio_data(data_str):
    # Carregar dados
    dados = []
    with open('../data/compilado_dados.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['timestamp'] and ('presenca' in row['entity_id'] or 'occupancy' in row['entity_id']):
                try:
                    dt = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                    dados.append({
                        'timestamp': dt,
                        'hour': dt.hour,
                        'date': dt.date(),
                        'weekday': dt.strftime('%A'),
                        'new_state': row.get('new_state', ''),
                        'friendly_name': json.loads(row['attributes']).get('friendly_name', '').lower() if row['attributes'] else ''
                    })
                except:
                    continue
    
    # Filtrar por data
    data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    dados_data = [d for d in dados if d['date'] == data_obj and d['new_state'] == 'on']
    
    if not dados_data:
        return None
    
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
    
    return {
        'data': data_str,
        'weekday': dados_data[0]['weekday'],
        'total': len(dados_data),
        'locais': locais_map,
        'dados': dados_data
    }

# Gerar relatórios para todas as datas
relatorios = []
for data in DATAS_PARA_ANALISAR:
    rel = gerar_relatorio_data(data)
    if rel:
        relatorios.append(rel)

# HTML comparativo
html = """<!DOCTYPE html>
<html>
<head>
    <title>Análise Comparativa - Múltiplas Datas</title>
    <style>
        body { font-family: Arial; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .comparativo { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .card { background: #f8f9fa; padding: 20px; border-radius: 10px; }
        .heatmap-mini { display: grid; grid-template-columns: repeat(24, 1fr); gap: 1px; margin: 10px 0; }
        .cell-mini { height: 15px; border-radius: 2px; }
        .stats { display: flex; justify-content: space-around; margin: 15px 0; }
        .stat { text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Análise Comparativa - Smart Home</h1>
        
        <div class="comparativo">"""

cores = {'Quarto': '#2196F3', 'Sala': '#4CAF50', 'Cozinha': '#FF9800', 'Banheiro': '#F44336'}

for rel in relatorios:
    html += f"""<div class="card">
                    <h3>{rel['weekday']}, {rel['data']}</h3>
                    <div class="stats">
                        <div class="stat">
                            <div style="font-size: 20px; font-weight: bold; color: #2196F3;">{rel['total']}</div>
                            <div>Detecções</div>
                        </div>
                    </div>"""
    
    # Mini heatmap por local
    for local in ['Quarto', 'Sala', 'Cozinha', 'Banheiro']:
        html += f'<div><strong>{local}</strong></div><div class="heatmap-mini">'
        if local in rel['locais']:
            freq_hora = {}
            for d in rel['locais'][local]:
                freq_hora[d['hour']] = freq_hora.get(d['hour'], 0) + 1
            max_freq = max(freq_hora.values()) if freq_hora else 1
            for h in range(24):
                freq = freq_hora.get(h, 0)
                opacity = (freq / max_freq * 0.8 + 0.2) if freq > 0 else 0.1
                html += f'<div class="cell-mini" style="background-color: {cores[local]}; opacity: {opacity};" title="{h}:00 - {freq}"></div>'
        else:
            for h in range(24):
                html += '<div class="cell-mini" style="background-color: #eee;"></div>'
        html += '</div>'
    
    html += '</div>'

html += """</div>
        
        <h2>📋 Resumo Comparativo</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #ddd;">Data</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Dia da Semana</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Total</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Quarto</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Sala</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Cozinha</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Banheiro</th>
            </tr>"""

for rel in relatorios:
    html += f"""<tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{rel['data']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{rel['weekday']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{rel['total']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{len(rel['locais'].get('Quarto', []))}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{len(rel['locais'].get('Sala', []))}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{len(rel['locais'].get('Cozinha', []))}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{len(rel['locais'].get('Banheiro', []))}</td>
            </tr>"""

html += """</table>
    </div>
</body>
</html>"""

with open('comparativo_multiplas_datas.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Relatórios gerados:")
for rel in relatorios:
    print(f"  {rel['data']} ({rel['weekday']}): {rel['total']} detecções")
print(f"\nComparativo salvo: comparativo_multiplas_datas.html")