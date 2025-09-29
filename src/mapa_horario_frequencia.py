import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# Carregar os dados
df = pd.read_csv("data/compilado_dados.csv")

# Converter timestamp para datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Extrair data e hora
df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour

# Pegar apenas uma data específica (primeira data disponível)
primeira_data = df['date'].min()
print(f"Analisando dados da data: {primeira_data}")

# Filtrar dados para essa data
df_data = df[df['date'] == primeira_data].copy()

# Identificar os principais sensores (top 10 por frequência)
principais_sensores = df_data['entity_id'].value_counts().head(10)
print(f"\nPrincipais sensores na data {primeira_data}:")
print(principais_sensores)

# Filtrar apenas os principais sensores
df_principais = df_data[df_data['entity_id'].isin(principais_sensores.index)].copy()

# Criar matriz de frequência por hora para cada sensor
horas = range(24)
matriz_freq = pd.DataFrame(index=principais_sensores.index, columns=horas, dtype=int)
matriz_freq = matriz_freq.fillna(0)

# Preencher a matriz com as frequências
for sensor in principais_sensores.index:
    sensor_data = df_principais[df_principais['entity_id'] == sensor]
    freq_por_hora = sensor_data.groupby('hour').size()
    for hora, freq in freq_por_hora.items():
        matriz_freq.loc[sensor, hora] = freq

# Criar o mapa de calor
plt.figure(figsize=(16, 10))
sns.heatmap(matriz_freq, 
            annot=True, 
            fmt='d', 
            cmap='YlOrRd',
            cbar_kws={'label': 'Frequência de Ativações'},
            xticklabels=[f'{h:02d}:00' for h in horas])

plt.title(f'Mapa de Horário e Frequência dos Principais Sensores\nData: {primeira_data}', 
          fontsize=16, fontweight='bold')
plt.xlabel('Hora do Dia', fontsize=12)
plt.ylabel('Sensores', fontsize=12)
plt.xticks(rotation=45)
plt.yticks(rotation=0)

# Ajustar labels dos sensores para melhor visualização
sensor_labels = []
for sensor in matriz_freq.index:
    # Simplificar nomes dos sensores
    if 'automation' in sensor:
        label = sensor.replace('automation.', '').replace('_', ' ')
    elif 'sensor' in sensor:
        label = sensor.replace('sensor.', '').replace('_', ' ')
    elif 'binary_sensor' in sensor:
        label = sensor.replace('binary_sensor.', '').replace('_', ' ')
    else:
        label = sensor.replace('_', ' ')
    sensor_labels.append(label[:30])  # Limitar tamanho

plt.gca().set_yticklabels(sensor_labels)
plt.tight_layout()
plt.savefig('../data/mapa_horario_frequencia.png', dpi=300, bbox_inches='tight')
plt.show()

# Estatísticas resumidas
print(f"\nEstatísticas da data {primeira_data}:")
print(f"Total de eventos: {len(df_data)}")
print(f"Número de sensores únicos: {df_data['entity_id'].nunique()}")
print(f"Horário com mais atividade: {df_data['hour'].mode().iloc[0]}:00")
print(f"Sensor mais ativo: {principais_sensores.index[0]} ({principais_sensores.iloc[0]} eventos)")

# Análise por período do dia
df_data['periodo'] = pd.cut(df_data['hour'], 
                           bins=[0, 6, 12, 18, 24], 
                           labels=['Madrugada (0-6h)', 'Manhã (6-12h)', 
                                  'Tarde (12-18h)', 'Noite (18-24h)'],
                           include_lowest=True)

print(f"\nDistribuição por período do dia:")
periodo_stats = df_data['periodo'].value_counts().sort_index()
for periodo, count in periodo_stats.items():
    print(f"{periodo}: {count} eventos ({count/len(df_data)*100:.1f}%)")