import numpy as np
import yaml
import os
from ecmwfapi import ECMWFDataServer
from ecmwf.opendata import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv

FILE_PATH = '../DATA/'
steps = list(range(0, 145, 3)) + list(range(150, 241, 6))
client = Client(source="ecmwf")

params = {'temperatura': '2t', 'precipitacion': 'tp', 'solar': 'ssr'}

for param in params.keys():
    request_latest_update = {
    "type": "fc",
    "step": steps,
    "param": params[param],
    }
    lastest_update = client.latest(request_latest_update)
    lastest_update_hour = lastest_update.hour

    request = {
    "time": lastest_update_hour,
    "type": "fc",
    "step": steps,
    "param": params[param]
    }
    relative_day = 0 if lastest_update_hour in (00,18) else 1
    FILENAME = "".join(['data_', param, '_', str(datetime.today().date() + timedelta(relative_day)), '.grib2'])
    client.retrieve(request, FILE_PATH+FILENAME)

# Ahora vamos a eliminar los archivos mas antiguos y quedarnos solo con los ultimos

archivos = {}
for variable in list(params.keys()):
    archivos[variable] = [filename for filename in os.listdir(FILE_PATH) if variable in filename]

# Función para extraer la fecha del nombre del archivo
def extraer_fecha(nombre_archivo):
    # Dividir el nombre del archivo por "_" y "." para extraer la fecha
    partes = nombre_archivo.split('_')
    fecha_str = partes[-1].split('.')[0]  # Extraer la parte de la fecha
    return datetime.strptime(fecha_str, '%Y-%m-%d')  # Convertir la fecha a formato datetime

# Eliminar archivos antiguos
for variable, lista_archivos in archivos.items():
    # Encontrar el archivo con la fecha más reciente
    archivo_mas_reciente = max(lista_archivos, key=extraer_fecha)
    
    # Iterar sobre los archivos de la variable
    for archivo in lista_archivos:
        # Si el archivo no es el más reciente, se elimina
        if extraer_fecha(archivo) < extraer_fecha(archivo_mas_reciente):
            print(f"Eliminando archivo: {archivo}")  # Mensaje opcional
            os.remove(FILE_PATH + archivo)  # Eliminar el archivo físicamente del sistema

    # Actualizar el diccionario para mantener solo el archivo más reciente
    archivos[variable] = [archivo_mas_reciente]

print(f'Nos quedamos con los archivos: \n {archivos}')
