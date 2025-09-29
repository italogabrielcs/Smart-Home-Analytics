import csv
from datetime import datetime, timedelta
import json

# CONFIGURAÇÃO - MUDE APENAS ESTA VARIÁVEL
DATA_ESCOLHIDA = "2025-08-17"  # Formato: YYYY-MM-DD

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
                    'minute': dt.minute,
                    'date': dt.date(),
                    'new_state': row.get('new_state', ''),
                    'friendly_name': json.loads(row['attributes']).get('friendly_name', '').lower() if row['attributes'] else ''
                })
            except:
                continue

# Filtrar por data escolhida
data_obj = datetime.strptime(DATA_ESCOLHIDA, "%Y-%m-%d").date()
dados_data = [d for d in dados if d['date'] == data_obj and d['new_state'] == 'on']
dados_data.sort(key=lambda x: x['timestamp'])

# Mapear locais
def get_local(friendly_name):
    if 'quarto' in friendly_name: return 'Quarto'
    elif 'sala' in friendly_name: return 'Sala'
    elif 'cozinha' in friendly_name: return 'Cozinha'
    elif 'banheiro' in friendly_name: return 'Banheiro'
    return 'Outro'

# Criar sequência de movimentos
sequencia = []
for d in dados_data:
    local = get_local(d['friendly_name'])
    if local != 'Outro':
        sequencia.append({
            'hora': f"{d['hour']:02d}:{d['minute']:02d}",
            'local': local,
            'timestamp': d['timestamp']
        })

# Agrupar movimentos próximos (mesmo local em 5 min)
movimentos = []
if sequencia:
    atual = sequencia[0]
    for prox in sequencia[1:]:
        if (prox['local'] != atual['local'] or 
            (prox['timestamp'] - atual['timestamp']).seconds > 300):
            movimentos.append(atual)
            atual = prox
    movimentos.append(atual)

# Gerar HTML com sequência
html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Sequência de Movimento - {DATA_ESCOLHIDA}</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); max-width: 1000px; margin: 0 auto; }}
        .timeline {{ position: relative; margin: 30px 0; }}
        .movimento {{ display: flex; align-items: center; margin: 15px 0; }}
        .hora {{ background: #333; color: white; padding: 8px 15px; border-radius: 20px; min-width: 60px; text-align: center; }}
        .seta {{ margin: 0 15px; font-size: 20px; color: #666; }}
        .local {{ padding: 10px 20px; border-radius: 25px; font-weight: bold; color: white; }}
        .quarto {{ background: #2196F3; }}
        .sala {{ background: #4CAF50; }}
        .cozinha {{ background: #FF9800; }}
        .banheiro {{ background: #F44336; }}
        .fluxo {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; align-items: center; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚶 Sequência de Movimento pela Casa</h1>
        <h2>📅 {DATA_ESCOLHIDA}</h2>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📊 Total Movimentos</h3>
                <div style="font-size: 24px; font-weight: bold; color: #2196F3;">{len(movimentos)}</div>
            </div>
            <div class="stat-card">
                <h3>⏰ Primeiro Movimento</h3>
                <div style="font-size: 18px; font-weight: bold;">{movimentos[0]['hora'] if movimentos else 'N/A'}</div>
            </div>
            <div class="stat-card">
                <h3>🌙 Último Movimento</h3>
                <div style="font-size: 18px; font-weight: bold;">{movimentos[-1]['hora'] if movimentos else 'N/A'}</div>
            </div>
        </div>
        
        <h3>🔄 Fluxo de Movimento</h3>
        <div class="fluxo">"""

for i, mov in enumerate(movimentos):
    local_class = mov['local'].lower()
    html += f'<div class="local {local_class}">{mov["hora"]} - {mov["local"]}</div>'
    if i < len(movimentos) - 1:
        html += '<div class="seta">→</div>'

html += """</div>
        
        <h3>📋 Timeline Detalhada</h3>
        <div class="timeline">"""

for mov in movimentos:
    local_class = mov['local'].lower()
    html += f"""<div class="movimento">
                    <div class="hora">{mov['hora']}</div>
                    <div class="seta">→</div>
                    <div class="local {local_class}">{mov['local']}</div>
                </div>"""

# Análise de padrões
locais_visitados = [m['local'] for m in movimentos]
transicoes = {}
for i in range(len(locais_visitados) - 1):
    origem = locais_visitados[i]
    destino = locais_visitados[i + 1]
    if origem != destino:
        chave = f"{origem} → {destino}"
        transicoes[chave] = transicoes.get(chave, 0) + 1

html += """</div>
        
        <h3>🔄 Transições Mais Comuns</h3>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">"""

for transicao, count in sorted(transicoes.items(), key=lambda x: x[1], reverse=True)[:5]:
    html += f'<div style="margin: 10px 0; padding: 10px; background: white; border-radius: 5px;">{transicao}: <strong>{count} vezes</strong></div>'

html += f"""</div>
        
        <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
            <p>Para mudar a data, edite a variável DATA_ESCOLHIDA no código</p>
        </div>
    </div>
</body>
</html>"""

with open(f'sequencia_{DATA_ESCOLHIDA}.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Sequência gerada: sequencia_{DATA_ESCOLHIDA}.html")
print(f"Total de movimentos: {len(movimentos)}")
if movimentos:
    print(f"Primeiro movimento: {movimentos[0]['hora']} - {movimentos[0]['local']}")
    print(f"Último movimento: {movimentos[-1]['hora']} - {movimentos[-1]['local']}")
    print("\nTransições mais comuns:")
    for transicao, count in sorted(transicoes.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"  {transicao}: {count} vezes")