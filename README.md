# Validador de duplicados en JSON

* Acepta un directorio con los JSON como parámetro 
* Crea un directorio nuevo con el sufijo "_sin_duplicados"
* Procesa todos los archivos JSON del directorio
* Genera un archivo CSV con el resumen de todos los archivos procesados

```CMD 
python check_duplicates.py <ruta_directorio>
```

```CMD 
python check_duplicates_by_fields.py <ruta_directorio> <campo1> <campo2> ...
```

* Acepta un directorio con los JSON como parámetro
* Procesa todos los archivos JSON del directorio
* Genera un archivo CSV con el resumen de todos los archivos procesados indicando si su id o lista de campos estan duplicados

```CMD 
python check_duplicates_across_files.py <ruta_directorio>
```

```CMD 
python check_duplicates_across_files.py <ruta_directorio> <campo1> <campo2> ...
```
