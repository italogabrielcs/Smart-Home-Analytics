import csv
from datetime import datetime
from collections import defaultdict, Counter
import json

# Função para ler e processar os dados
def processar_dados():
    dados = []
    
    # Ler o arquivo CSV
    with open('../data/compilado_dados.csv', 'r', encoding='utf-8') as file:
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
                        'hour': timestamp.hour
                    })
                except:
                    continue
    
    return dados

# Processar dados
print("Carregando dados...")
dados = processar_dados()
print(f"Total de registros carregados: {len(dados)}")

# Pegar a primeira data disponível
primeira_data = min(d['date'] for d in dados)
print(f"Analisando dados da data: {primeira_data}")

# Filtrar dados para essa data
dados_data = [d for d in dados if d['date'] == primeira_data]
print(f"Registros na data {primeira_data}: {len(dados_data)}")

# Identificar os principais sensores (top 10)
contador_sensores = Counter(d['entity_id'] for d in dados_data)
principais_sensores = contador_sensores.most_common(10)

print(f"\nPrincipais sensores na data {primeira_data}:")
for i, (sensor, freq) in enumerate(principais_sensores, 1):
    print(f"{i:2d}. {sensor}: {freq} eventos")

# Criar matriz de frequência por hora
matriz_freq = {}
for sensor, _ in principais_sensores:
    matriz_freq[sensor] = [0] * 24

# Preencher matriz
for dado in dados_data:
    if dado['entity_id'] in [s[0] for s in principais_sensores]:
        matriz_freq[dado['entity_id']][dado['hour']] += 1

# Exibir mapa de frequência em formato texto
print(f"\n{'='*80}")
print(f"MAPA DE HORÁRIO E FREQUÊNCIA - {primeira_data}")
print(f"{'='*80}")

# Cabeçalho das horas
print("Sensor".ljust(35), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()

print("-" * 80)

# Dados dos sensores
for sensor, _ in principais_sensores:
    # Simplificar nome do sensor
    nome_simples = sensor.replace('automation.', '').replace('sensor.', '').replace('binary_sensor.', '')
    nome_simples = nome_simples.replace('_', ' ')[:30]
    
    print(nome_simples.ljust(35), end="")
    for freq in matriz_freq[sensor]:
        if freq == 0:
            print("  .", end="")
        else:
            print(f"{freq:3d}", end="")
    print()

# Estatísticas por período do dia
print(f"\n{'='*50}")
print("ANÁLISE POR PERÍODO DO DIA")
print(f"{'='*50}")

periodos = {
    'Madrugada (0-6h)': [0, 1, 2, 3, 4, 5],
    'Manhã (6-12h)': [6, 7, 8, 9, 10, 11],
    'Tarde (12-18h)': [12, 13, 14, 15, 16, 17],
    'Noite (18-24h)': [18, 19, 20, 21, 22, 23]
}

contador_periodos = Counter()
for dado in dados_data:
    for periodo, horas in periodos.items():
        if dado['hour'] in horas:
            contador_periodos[periodo] += 1
            break

total_eventos = len(dados_data)
for periodo, count in contador_periodos.items():
    percentual = (count / total_eventos) * 100
    print(f"{periodo}: {count:4d} eventos ({percentual:5.1f}%)")

# Horário de pico
contador_horas = Counter(d['hour'] for d in dados_data)
hora_pico = contador_horas.most_common(1)[0]
print(f"\nHorário de maior atividade: {hora_pico[0]:02d}:00 ({hora_pico[1]} eventos)")

# Sensor mais ativo
sensor_mais_ativo = principais_sensores[0]
print(f"Sensor mais ativo: {sensor_mais_ativo[0]} ({sensor_mais_ativo[1]} eventos)")

print(f"\n{'='*80}")
print("Legenda: '.' = 0 eventos, números = quantidade de eventos")
print(f"{'='*80}")