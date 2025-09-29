import csv
import glob
import os

# Encontrar todos os arquivos CSV
arquivos = glob.glob('data/2025-08-16/*.csv')
print(f"Encontrados {len(arquivos)} arquivos")

# Criar arquivo compilado
with open('data/compilado_dados.csv', 'w', newline='', encoding='utf-8') as saida:
    writer = None
    
    for arquivo in arquivos:
        with open(arquivo, 'r', encoding='utf-8') as entrada:
            reader = csv.DictReader(entrada)
            
            if writer is None:
                writer = csv.DictWriter(saida, fieldnames=reader.fieldnames)
                writer.writeheader()
            
            for row in reader:
                writer.writerow(row)

print("Arquivo compilado_dados.csv criado com sucesso!")