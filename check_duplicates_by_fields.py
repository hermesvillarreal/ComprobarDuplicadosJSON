import json
import sys
import csv
from collections import Counter
from pathlib import Path

def process_json_file_by_fields(file_path, fields, output_dir, summary_data):
    try:
        # Leer el archivo JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if not isinstance(data, list):
            print("Error: El archivo JSON debe contener una lista de registros")
            return
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: El archivo {file_path} no es un JSON válido")
        return
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return
        
    # Crear tuplas con solo los campos especificados
    def get_fields_tuple(record):
        return tuple(sorted((k, record[k]) for k in fields if k in record))
    
    records_by_fields = [get_fields_tuple(record) for record in data]
    
    # Contar ocurrencias
    count = Counter(records_by_fields)
    
    # Obtener duplicados
    duplicates = {k: v for k, v in count.items() if v > 1}
    
    # Estadísticas
    total_records = len(data)
    unique_records = len(set(records_by_fields))
    duplicate_count = total_records - unique_records
    
    # Mostrar resultados
    print(f"\nEstadísticas del archivo JSON:")
    print(f"Campos analizados: {', '.join(fields)}")
    print(f"Total de registros: {total_records}")
    print(f"Registros duplicados: {duplicate_count}")
    
    # Crear archivo sin duplicados en el directorio de salida
    output_file = output_dir / file_path.name
    
    # Mantener solo un registro de cada grupo de duplicados
    seen = set()
    unique_records = []
    for record_fields, record in zip(records_by_fields, data):
        if record_fields not in seen:
            seen.add(record_fields)
            unique_records.append(record)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_records, f, indent=2, ensure_ascii=False)
    
    print(f"\nArchivo sin duplicados generado: {output_file}")

    if duplicates:
        print("\nRegistros duplicados encontrados:")
        # Crear un diccionario para mapear las tuplas de campos a sus registros completos
        duplicate_records = {}
        for i, record_fields in enumerate(records_by_fields):
            if record_fields in duplicates:
                if record_fields not in duplicate_records:
                    duplicate_records[record_fields] = []
                duplicate_records[record_fields].append(data[i])
        
        for fields_tuple, records in duplicate_records.items():
            print(f"\nRegistros con valores duplicados (aparece {len(records)} veces):")
            for record in records:
                print(json.dumps(record, indent=2, ensure_ascii=False))
        
        # Guardar información para el resumen
        summary_data.append({
            'archivo': file_path.name,
            'campos_analizados': ', '.join(fields),
            'registros_totales': total_records,
            'registros_duplicados': duplicate_count,
            'registros_unicos': len(unique_records)
        })
    else:
        print("\nNo se encontraron registros duplicados")
        # Guardar información para el resumen sin duplicados
        summary_data.append({
            'archivo': file_path.name,
            'campos_analizados': ', '.join(fields),
            'registros_totales': total_records,
            'registros_duplicados': 0,
            'registros_unicos': total_records
        })

def process_directory(input_dir, fields):
    # Convertir el input a Path
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"Error: {input_dir} no es un directorio válido")
        return

    # Crear directorio de salida
    output_dir = input_path.parent / f"{input_path.name}_sin_duplicados"
    output_dir.mkdir(exist_ok=True)

    # Lista para almacenar el resumen de cada archivo
    summary_data = []

    # Procesar cada archivo JSON en el directorio
    json_files = list(input_path.glob('*.json'))
    if not json_files:
        print(f"No se encontraron archivos JSON en {input_dir}")
        return

    for json_file in json_files:
        print(f"\nProcesando archivo: {json_file.name}")
        process_json_file_by_fields(json_file, fields, output_dir, summary_data)

    # Generar archivo CSV con el resumen
    csv_file = output_dir / 'resumen_duplicados.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['archivo', 'campos_analizados', 
                                             'registros_totales', 'registros_duplicados', 
                                             'registros_unicos'])
        writer.writeheader()
        writer.writerows(summary_data)

    print(f"\nResumen generado en: {csv_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python check_duplicates_by_fields.py <ruta_directorio> <campo1> <campo2> ...")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    fields = sys.argv[2:]
    process_directory(dir_path, fields)
