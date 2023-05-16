#!/usr/bin/env python
'''
Actualizar Sitios en la Lista Negra 2.0
'''
import os
import sys
import django
from time import asctime
from configparser import ConfigParser
from funciones import obtener_ruta_configuraciones, depurar_dominios


# Cargar configuraciones
config_parser = ConfigParser()
config_parser.read(os.path.join(
  obtener_ruta_configuraciones(), 'principal.conf'))
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Directivas del Filtro
DirectorioListasNegrasActualizacion = config_parser.get(
  'FiltroWeb', 'DirectorioListasNegrasActualizacion')

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importes de Django
# pylint: disable=wrong-import-position
from django.db import connection
from Administrador.models import Categoria, Sitio
# pylint: enable=wrong-import-position

try:
  # Inicio
  print('Inicio: ', asctime())

  # Variables de sesion
  contenidos = []
  elementos = []

  # Truncar tabla con los sitios para ingresar los nuevos registros
  cursor = connection.cursor()
  # pylint: disable=protected-access
  cursor.execute(f'TRUNCATE TABLE "{Sitio._meta.db_table}"')
  # pylint: enable=protected-access
  cursor.close()

  # Procesamiento, Ingreso y Ordenacion de las listas negras en la BD
  categorias = Categoria.objects.all()
  for c in categorias:
    # Inicio de Categoria
    print(f'Procesando {c.nombre} ......'),

    # Reiniciar las variables de sesion
    del contenidos[:]
    del elementos[:]

    # Procesamos el archivo de texto con los dominios
    rutac = os.path.join(DirectorioListasNegrasActualizacion, c.ruta, 'domains')
    with open(rutac, 'r', encoding='utf-8') as archivo:
      contenidos = depurar_dominios(archivo.read())

    # Convertimos en una lista de modelos tipo Sitio
    for registro in contenidos:
      elementos.append(Sitio(categoria=c, dominio=registro))

    # Los metemos en la base de datos en grupos de 1000 registros
    Sitio.objects.bulk_create(elementos, batch_size=1000)

    # Fin de Categoria
    print(f'{len(elementos)} registros')

  # Fin
  print('Fin: ', asctime())

except Exception as e:
  print(f'{str(type(e))}: {str(e)}')
