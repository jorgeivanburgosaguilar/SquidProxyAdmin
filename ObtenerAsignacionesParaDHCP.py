#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Obtener Asignaciones para DHCP
# Genera las asignaciones configuradas en la base de datos para DHCP (Dnsmasq)
import os
import sys
from ConfigParser import SafeConfigParser
from Funciones import obtener_ruta_configuraciones


# Cargar configuraciones
configParser = SafeConfigParser()
configParser.read(os.path.join(obtener_ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
en_produccion = configParser.getboolean('FiltroWeb', 'Produccion')

# Cargar backend basado en Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importes de Django
from Administrador.models import Asignacion

try:
    asignaciones = Asignacion.objects.all().values('ip', 'mac')
    for asignacion in asignaciones:
        sys.stdout.write('dhcp-host={0},192.168.2.{1}\n'.format(asignacion['mac'].upper(), asignacion['ip']))


except Exception as e:
    if not en_produccion:
        sys.stdout.write('{0}: {1}'.format(str(type(e)), str(e)))
