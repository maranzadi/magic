import csv

# Abrir el CSV
with open('ManaBox_Collection.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)  # Usamos DictReader para acceder por nombre de columna
    
    # Abrir el archivo de texto para escribir
    with open('scryfall_ids.txt', 'w', encoding='utf-8') as txtfile:
        for row in reader:
            scryfall_id = row['Scryfall ID']  # Obtener solo la columna deseada
            if scryfall_id:  # Evitar filas vacías
                txtfile.write(scryfall_id + '\n')

print("Columna 'Scryfall ID' guardada en scryfall_ids.txt, una ID por línea.")
