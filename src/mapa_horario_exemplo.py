import csv
from datetime import datetime
from collections import defaultdict, Counter
import json
import os

# Função para ler e processar os dados de um arquivo específico
def processar_dados(arquivo_csv):
    dados = []
    
    # Ler o arquivo CSV
    with open(arquivo_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['timestamp']:  # Verificar se timestamp não está vazio
                try:
                    # Converter timestamp
                    timestamp = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                    dados.append({
                        'entity_id': row['entity_id'],
                        'timestamp': timestamp,
                        'date': timestamp.date(),
                        'hour': timestamp.hour,
                        'old_state': row.get('old_state', ''),
                        'new_state': row.get('new_state', '')
                    })
                except Exception as e:
                    continue
    
    return dados

# Pegar um arquivo de exemplo
arquivo_exemplo = '../data/2025-08-17/01.csv'
print(f"Analisando arquivo: {arquivo_exemplo}")

# Processar dados
dados = processar_dados(arquivo_exemplo)
print(f"Total de registros carregados: {len(dados)}")

if len(dados) == 0:
    print("Nenhum dado válido encontrado!")
    exit()

# Pegar a data dos dados
data_analise = dados[0]['date']
print(f"Data dos dados: {data_analise}")

# Identificar os principais sensores (top 10)
contador_sensores = Counter(d['entity_id'] for d in dados)
principais_sensores = contador_sensores.most_common(10)

print(f"\nPrincipais sensores:")
for i, (sensor, freq) in enumerate(principais_sensores, 1):
    print(f"{i:2d}. {sensor}: {freq} eventos")

# Criar matriz de frequência por hora
matriz_freq = {}
for sensor, _ in principais_sensores:
    matriz_freq[sensor] = [0] * 24

# Preencher matriz
for dado in dados:
    if dado['entity_id'] in [s[0] for s in principais_sensores]:
        matriz_freq[dado['entity_id']][dado['hour']] += 1

# Exibir mapa de frequência em formato texto
print(f"\n{'='*100}")
print(f"MAPA DE HORÁRIO E FREQUÊNCIA DOS PRINCIPAIS SENSORES - {data_analise}")
print(f"{'='*100}")

# Cabeçalho das horas
print("Sensor".ljust(40), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()

print("-" * 100)

# Dados dos sensores
for sensor, _ in principais_sensores:
    # Simplificar nome do sensor
    nome_simples = sensor.replace('automation.', '').replace('sensor.', '').replace('binary_sensor.', '')
    nome_simples = nome_simples.replace('_', ' ')[:35]
    
    print(nome_simples.ljust(40), end="")
    for freq in matriz_freq[sensor]:
        if freq == 0:
            print("  .", end="")
        else:
            print(f"{freq:3d}", end="")
    print(f" | Total: {sum(matriz_freq[sensor])}")

# Estatísticas por período do dia
print(f"\n{'='*60}")
print("ANÁLISE POR PERÍODO DO DIA")
print(f"{'='*60}")

periodos = {
    'Madrugada (0-6h)': [0, 1, 2, 3, 4, 5],
    'Manhã (6-12h)': [6, 7, 8, 9, 10, 11],
    'Tarde (12-18h)': [12, 13, 14, 15, 16, 17],
    'Noite (18-24h)': [18, 19, 20, 21, 22, 23]
}

contador_periodos = Counter()
for dado in dados:
    for periodo, horas in periodos.items():
        if dado['hour'] in horas:
            contador_periodos[periodo] += 1
            break

total_eventos = len(dados)
for periodo, count in contador_periodos.items():
    percentual = (count / total_eventos) * 100
    print(f"{periodo}: {count:4d} eventos ({percentual:5.1f}%)")

# Horário de pico
contador_horas = Counter(d['hour'] for d in dados)
horas_ordenadas = contador_horas.most_common(5)
print(f"\nTop 5 horários com mais atividade:")
for i, (hora, count) in enumerate(horas_ordenadas, 1):
    print(f"{i}. {hora:02d}:00 - {count} eventos")

# Sensor mais ativo
sensor_mais_ativo = principais_sensores[0]
print(f"\nSensor mais ativo: {sensor_mais_ativo[0]} ({sensor_mais_ativo[1]} eventos)")

# Análise de estados (on/off) para sensores binários
print(f"\n{'='*60}")
print("ANÁLISE DE ESTADOS (ON/OFF)")
print(f"{'='*60}")

estados_on = Counter()
estados_off = Counter()

for dado in dados:
    if dado['entity_id'] in [s[0] for s in principais_sensores[:5]]:  # Top 5 sensores
        if dado['new_state'] == 'on':
            estados_on[dado['entity_id']] += 1
        elif dado['new_state'] == 'off':
            estados_off[dado['entity_id']] += 1

for sensor, _ in principais_sensores[:5]:
    on_count = estados_on.get(sensor, 0)
    off_count = estados_off.get(sensor, 0)
    total = on_count + off_count
    if total > 0:
        nome_simples = sensor.replace('automation.', '').replace('sensor.', '').replace('binary_sensor.', '')
        nome_simples = nome_simples.replace('_', ' ')[:30]
        print(f"{nome_simples.ljust(30)}: ON={on_count:3d} OFF={off_count:3d} Total={total:3d}")

print(f"\n{'='*100}")
print("Legenda: '.' = 0 eventos, números = quantidade de eventos por hora")
print("Este mapa mostra a atividade dos sensores ao longo de 24 horas")
print(f"{'='*100}")