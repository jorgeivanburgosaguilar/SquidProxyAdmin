#!/usr/bin/env python
'''
Actualizar Sitios en la Listas de Bloqueo 2.0
'''
import os
import sys
import django
from django.db import connection
from time import asctime
from funciones import procesar_tlds, depurar_dominios


# Agregar directorio actual a las rutas del entorno
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importar modelos
from Administrador.models import Categoria, Sitio

# Configuraciones y mensajes de error
DIRECTORIOLISTABLOQUEO = os.getenv('SQUIDPROXYADM_DIRLISTABLOQUEO')

# Variables
TLDS = procesar_tlds()

try:
  print('Inicio: ', asctime())

  # Variables de sesion
  contenidos = []
  elementos = []

  # Truncar tabla con los sitios para ingresar los nuevos registros
  # TODO Implementar actualizacion diferencial
  # pylint: disable=protected-access
  cursor = connection.cursor()
  cursor.execute(f'TRUNCATE TABLE "{Sitio._meta.db_table}"')
  cursor.close()
  # pylint: enable=protected-access

  # Procesamiento, Ingreso y Ordenacion de las listas de bloqueo en la BD
  categorias = Categoria.objects.all()
  for c in categorias:
    print(f'Procesando {c.nombre} ......', end='')

    # Reiniciar las variables de sesion
    del contenidos[:]
    del elementos[:]

    # Procesamos el archivo de texto con los dominios
    rutac = os.path.join(DIRECTORIOLISTABLOQUEO, c.ruta, 'domains')
    with open(rutac, 'r', encoding='utf-8') as archivo:
      contenidos = depurar_dominios(archivo.read(), TLDS)

    # Convertimos en una lista de modelos tipo Sitio
    for registro in contenidos:
      elementos.append(Sitio(categoria=c, dominio=registro))

    # Los metemos en la base de datos en grupos de 1,000 registros
    Sitio.objects.bulk_create(elementos, batch_size=1000)

    # Fin de Categoria
    print(f'{len(elementos)} registros')

  print('Fin: ', asctime())

except Exception as e:
  print(f'{str(type(e))}: {str(e)}')
