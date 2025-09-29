import csv
from datetime import datetime
from collections import defaultdict, Counter
import json
import os
import glob

# Função para ler e processar os dados de múltiplos arquivos
def processar_multiplos_arquivos(pasta_dados):
    dados = []
    arquivos_csv = glob.glob(os.path.join(pasta_dados, "*.csv"))
    
    print(f"Encontrados {len(arquivos_csv)} arquivos CSV")
    
    for arquivo in arquivos_csv[:5]:  # Limitar a 5 arquivos para exemplo
        print(f"Processando: {arquivo}")
        with open(arquivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['timestamp']:
                    try:
                        timestamp = datetime.fromisoformat(row['timestamp'].replace('T', ' ').replace('+00:00', ''))
                        dados.append({
                            'entity_id': row['entity_id'],
                            'timestamp': timestamp,
                            'date': timestamp.date(),
                            'hour': timestamp.hour,
                            'old_state': row.get('old_state', ''),
                            'new_state': row.get('new_state', '')
                        })
                    except:
                        continue
    
    return dados

# Processar dados de múltiplos arquivos
pasta_dados = '../data/2025-08-17'
dados = processar_multiplos_arquivos(pasta_dados)
print(f"\nTotal de registros carregados: {len(dados)}")

if len(dados) == 0:
    print("Nenhum dado válido encontrado!")
    exit()

# Filtrar apenas sensores de presença e automações relevantes
sensores_interesse = []
for dado in dados:
    entity_id = dado['entity_id']
    if any(palavra in entity_id.lower() for palavra in ['presenca', 'motion', 'occupancy', 'auto_banheiro', 'aut_sala', 'aut_lampada']):
        sensores_interesse.append(dado)

print(f"Registros de sensores de interesse: {len(sensores_interesse)}")

# Se não houver sensores de presença, usar os mais frequentes
if len(sensores_interesse) < 50:
    contador_geral = Counter(d['entity_id'] for d in dados)
    top_sensores = [sensor for sensor, _ in contador_geral.most_common(10)]
    sensores_interesse = [d for d in dados if d['entity_id'] in top_sensores]
    print(f"Usando top 10 sensores mais frequentes: {len(sensores_interesse)} registros")

# Identificar os principais sensores
contador_sensores = Counter(d['entity_id'] for d in sensores_interesse)
principais_sensores = contador_sensores.most_common(8)

print(f"\nPrincipais sensores analisados:")
for i, (sensor, freq) in enumerate(principais_sensores, 1):
    print(f"{i:2d}. {sensor}: {freq} eventos")

# Criar matriz de frequência por hora
matriz_freq = {}
for sensor, _ in principais_sensores:
    matriz_freq[sensor] = [0] * 24

# Preencher matriz
for dado in sensores_interesse:
    if dado['entity_id'] in [s[0] for s in principais_sensores]:
        matriz_freq[dado['entity_id']][dado['hour']] += 1

# Exibir mapa de frequência
print(f"\n{'='*110}")
print(f"MAPA DE HORÁRIO E FREQUÊNCIA DOS PRINCIPAIS SENSORES")
print(f"{'='*110}")

# Cabeçalho das horas
print("Sensor".ljust(45), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print("  Total")

print("-" * 110)

# Dados dos sensores
for sensor, _ in principais_sensores:
    # Simplificar nome do sensor
    nome_simples = sensor.replace('automation.', '').replace('sensor.', '').replace('binary_sensor.', '')
    nome_simples = nome_simples.replace('_', ' ')[:40]
    
    print(nome_simples.ljust(45), end="")
    total_sensor = 0
    for freq in matriz_freq[sensor]:
        total_sensor += freq
        if freq == 0:
            print("  .", end="")
        else:
            print(f"{freq:3d}", end="")
    print(f"  {total_sensor:4d}")

# Totais por hora
print("-" * 110)
print("TOTAL POR HORA".ljust(45), end="")
totais_hora = [0] * 24
for h in range(24):
    total_h = sum(matriz_freq[sensor][h] for sensor, _ in principais_sensores)
    totais_hora[h] = total_h
    if total_h == 0:
        print("  .", end="")
    else:
        print(f"{total_h:3d}", end="")
print(f"  {sum(totais_hora):4d}")

# Análise de padrões
print(f"\n{'='*70}")
print("ANÁLISE DE PADRÕES DE ATIVIDADE")
print(f"{'='*70}")

# Períodos do dia
periodos = {
    'Madrugada (0-6h)': list(range(0, 6)),
    'Manhã (6-12h)': list(range(6, 12)),
    'Tarde (12-18h)': list(range(12, 18)),
    'Noite (18-24h)': list(range(18, 24))
}

print("Distribuição por período:")
for periodo, horas in periodos.items():
    total_periodo = sum(totais_hora[h] for h in horas)
    percentual = (total_periodo / sum(totais_hora)) * 100 if sum(totais_hora) > 0 else 0
    print(f"  {periodo}: {total_periodo:4d} eventos ({percentual:5.1f}%)")

# Horários de pico
print(f"\nTop 5 horários com mais atividade:")
horas_atividade = [(h, totais_hora[h]) for h in range(24)]
horas_atividade.sort(key=lambda x: x[1], reverse=True)

for i, (hora, total) in enumerate(horas_atividade[:5], 1):
    if total > 0:
        print(f"  {i}. {hora:02d}:00 - {total} eventos")

# Sensor mais ativo
if principais_sensores:
    sensor_top = principais_sensores[0]
    print(f"\nSensor mais ativo: {sensor_top[0]} ({sensor_top[1]} eventos)")

# Análise de estados para automações
print(f"\n{'='*70}")
print("ANÁLISE DE ESTADOS (ON/OFF) - AUTOMAÇÕES")
print(f"{'='*70}")

automacoes = [s for s, _ in principais_sensores if 'automation' in s]
if automacoes:
    for auto in automacoes[:5]:
        dados_auto = [d for d in sensores_interesse if d['entity_id'] == auto]
        on_count = sum(1 for d in dados_auto if d['new_state'] == 'on')
        off_count = sum(1 for d in dados_auto if d['new_state'] == 'off')
        
        nome_simples = auto.replace('automation.', '').replace('_', ' ')[:35]
        print(f"  {nome_simples.ljust(35)}: ON={on_count:3d} OFF={off_count:3d}")

print(f"\n{'='*110}")
print("INTERPRETAÇÃO:")
print("• Números mostram quantas vezes cada sensor foi ativado por hora")
print("• '.' indica nenhuma ativação naquele horário")
print("• Padrões podem indicar rotinas diárias e presença em casa")
print("• Automações mostram quando sistemas foram ligados/desligados")
print(f"{'='*110}")