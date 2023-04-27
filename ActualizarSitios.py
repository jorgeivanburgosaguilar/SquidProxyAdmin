#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Actualizar Sitios en la Lista Negra 2.0
import os
from time import asctime
from ConfigParser import SafeConfigParser
from Funciones import obtener_ruta_configuraciones, depurar_dominios


# Cargar configuraciones
configParser = SafeConfigParser()
configParser.read(os.path.join(obtener_ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
DirectorioListasNegrasActualizacion = configParser.get('FiltroWeb', 'DirectorioListasNegrasActualizacion')


# Cargar backend basado en Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importes de Django
from django.db import connection
from Administrador.models import Categoria, Sitio


try:
    # Inicio
    print 'Inicio: %s' % asctime()

    # Variables de sesion
    contenidos = []
    elementos = []

    # Truncar tabla con los sitios para ingresar los nuevos registros
    cursor = connection.cursor()
    cursor.execute('TRUNCATE TABLE "%s"' % Sitio._meta.db_table)
    cursor.close()

    # Procesamiento, Ingreso y Ordenacion de las listas negras en la BD
    categorias = Categoria.objects.all()
    for c in categorias:
        # Inicio de Categoria
        print 'Procesando %s ......' % c.nombre,

        # Reiniciar las variables de sesion
        del contenidos[:]
        del elementos[:]


        # Procesamos el archivo de texto con los dominios
        with open(os.path.join(DirectorioListasNegrasActualizacion, c.ruta, 'domains'), 'r') as archivo:
            contenidos = depurar_dominios(archivo.read())


        # Convertimos en una lista de modelos tipo Sitio
        for registro in contenidos:
            elementos.append(Sitio(categoria=c, dominio=registro))


        # Los metemos en la base de datos en grupos de 1000 registros
        Sitio.objects.bulk_create(elementos, batch_size=1000)


        # Fin de Categoria
        print '%s registros' % len(elementos)


    # Fin
    print 'Fin: %s' % asctime()

except Exception as e:
    print '{0}: {1}'.format(str(type(e)), str(e))
