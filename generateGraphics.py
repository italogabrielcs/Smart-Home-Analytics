import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados
df = pd.read_csv('dadosPresenca_tratados.csv')

# Filtra apenas sensores de presença dos cômodos desejados
comodos = [
    "binary_sensor.presenca_quarto_motion",
    "binary_sensor.presenca_cozinha_motion",
    "binary_sensor.presenca_sala_motion",
    "binary_sensor.presenca_banheiro_motion"
]

df_comodos = df[df['entity_id'].isin(comodos)]

# Conta entradas e saídas por cômodo
entradas = df_comodos[df_comodos['new_state'] == 'on'].groupby('entity_id').size()
saidas = df_comodos[df_comodos['new_state'] == 'off'].groupby('entity_id').size()

# Junta em um DataFrame para plotar
freq = pd.DataFrame({'Entradas': entradas, 'Saídas': saidas}).fillna(0)

# Renomeia para nomes mais amigáveis
nomes = {
    "binary_sensor.presenca_quarto_motion": "Quarto",
    "binary_sensor.presenca_cozinha_motion": "Cozinha",
    "binary_sensor.presenca_sala_motion": "Sala",
    "binary_sensor.presenca_banheiro_motion": "Banheiro"
}
freq.index = freq.index.map(nomes)

# Gráfico de barras
freq.plot(kind='bar', figsize=(10,6), color=['green', 'red'])
plt.ylabel('Frequência')
plt.title('Frequência de Entradas e Saídas por Cômodo (30 dias)')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()