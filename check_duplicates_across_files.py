import json
import csv
import zipfile
import rarfile
import os
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Union

def extract_compressed_files(input_dir: Path) -> None:
    """Extrae archivos JSON de archivos ZIP y RAR."""
    for ext, opener in [('*.zip', zipfile.ZipFile), ('*.rar', rarfile.RarFile)]:
        compressed_files = list(input_dir.glob(ext))
        if compressed_files:
            print(f"\nProcesando archivos {ext[1:].upper()}...")
            
        for file in compressed_files:
            try:
                with opener(file, 'r') as compressed:
                    # Listar solo archivos JSON
                    json_files = [f for f in compressed.namelist() if f.lower().endswith('.json')]
                    
                    if not json_files:
                        print(f"No se encontraron archivos JSON en {file.name}")
                        continue
                    
                    print(f"Extrayendo {len(json_files)} archivos JSON de {file.name}")
                    for json_file in json_files:
                        # Extraer solo el nombre del archivo
                        json_filename = Path(json_file).name
                        # Extraer al directorio de entrada
                        with compressed.open(json_file) as source, open(input_dir / json_filename, 'wb') as target:
                            target.write(source.read())
                            
            except Exception as e:
                print(f"Error procesando {file.name}: {str(e)}")

def load_json_files(directory: Path) -> List[tuple]:
    """Carga todos los archivos JSON y retorna una lista de tuplas (archivo, datos)."""
    json_files = list(directory.glob('*.json'))
    loaded_files = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    loaded_files.append((json_file.name, data))
                else:
                    print(f"Advertencia: {json_file.name} no contiene un diccionario JSON válido")
        except json.JSONDecodeError:
            print(f"Error: {json_file.name} no es un JSON válido")
        except Exception as e:
            print(f"Error procesando {json_file.name}: {str(e)}")
    
    return loaded_files

def find_duplicates_by_fields(files_data: List[tuple], fields: List[str]) -> Dict[str, Set[str]]:
    """Encuentra duplicados basados en campos específicos."""
    # Diccionario para almacenar archivos por valor de campos
    values_to_files = defaultdict(set)
    duplicates = defaultdict(set)
    
    for filename, data in files_data:
        # Crear una tupla con los valores de los campos especificados
        try:
            values = tuple(data[field] for field in fields)
            values_to_files[values].add(filename)
        except KeyError:
            print(f"Advertencia: {filename} no contiene todos los campos requeridos {fields}")
            continue
    
    # Encontrar duplicados
    for values, filenames in values_to_files.items():
        if len(filenames) > 1:
            # Agregar cada archivo y sus duplicados
            for filename in filenames:
                duplicates[filename] = filenames - {filename}
    
    return duplicates

def create_duplicate_report(duplicates: Dict[str, Set[str]], output_file: Path, fields: List[str]) -> None:
    """Genera un reporte CSV de duplicados."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Archivo', 'Campos Analizados', 'Tiene Duplicados', 'Duplicados Encontrados En'])
        
        # Ordenar archivos alfabéticamente
        for filename in sorted(set(duplicates.keys())):
            duplicate_files = sorted(duplicates[filename])
            writer.writerow([
                filename,
                ', '.join(fields),
                'Sí',
                ', '.join(duplicate_files)
            ])

def main(directory: Union[str, Path], fields: List[str] = None):
    if fields is None:
        fields = ['id']
    
    input_dir = Path(directory)
    if not input_dir.is_dir():
        print(f"Error: {directory} no es un directorio válido")
        return
    
    # Extraer archivos comprimidos
    ##extract_compressed_files(input_dir)
    
    # Cargar archivos JSON
    print("\nCargando archivos JSON...")
    files_data = load_json_files(input_dir)
    
    if not files_data:
        print("No se encontraron archivos JSON válidos para procesar")
        return
    
    print(f"\nBuscando duplicados basados en los campos: {fields}")
    duplicates = find_duplicates_by_fields(files_data, fields)
    
    if not duplicates:
        print("\nNo se encontraron duplicados")
        return
    
    # Crear reporte
    output_file = input_dir / 'reporte_duplicados.csv'
    create_duplicate_report(duplicates, output_file, fields)
    print(f"\nReporte generado en: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Para verificar solo por ID:")
        print("    python check_duplicates_across_files.py <directorio>")
        print("  Para verificar por múltiples campos:")
        print("    python check_duplicates_across_files.py <directorio> campo1 campo2 ...")
        sys.exit(1)
    
    directory = sys.argv[1]
    fields = sys.argv[2:] if len(sys.argv) > 2 else ['id']
    
    main(directory, fields)
