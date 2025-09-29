from collections import Counter
import random

# Simular dados de presença para outro dia (padrão diferente)
print("MAPA DE PRESENÇA - 2025-08-18 (Simulado)")
print("="*80)
print("Local".ljust(20), end="")
for h in range(24):
    print(f"{h:2d}".rjust(3), end="")
print()
print("-"*80)

# Padrões simulados para cada local
padroes = {
    'Quarto': [0,0,0,0,0,0,1,2,1,0,0,0,0,0,1,3,2,4,6,8,5,3,2,1],
    'Sala': [0,0,0,0,0,0,0,1,3,2,1,2,4,3,2,5,3,2,8,6,4,2,1,0],
    'Cozinha': [0,0,0,0,0,0,0,1,2,1,0,1,3,2,1,1,2,1,7,4,2,1,0,0],
    'Banheiro': [0,0,0,0,0,0,1,2,1,1,0,1,2,1,1,2,1,1,3,2,2,1,1,0]
}

for local, freq_horas in padroes.items():
    print(local.ljust(20), end="")
    for freq in freq_horas:
        print(f"{freq:3d}" if freq > 0 else "  .", end="")
    print()

print("="*80)
total = sum(sum(freq_horas) for freq_horas in padroes.values())
print(f"Total detecções: {total}")

# Horário de pico
hora_pico = 0
max_freq = 0
for h in range(24):
    freq_total = sum(padroes[local][h] for local in padroes)
    if freq_total > max_freq:
        max_freq = freq_total
        hora_pico = h

print(f"Horário pico: {hora_pico:02d}:00 ({max_freq} detecções)")

# Resumo por local
print("\nResumo por local:")
for local, freq_horas in padroes.items():
    total_local = sum(freq_horas)
    print(f"{local}: {total_local} detecções")