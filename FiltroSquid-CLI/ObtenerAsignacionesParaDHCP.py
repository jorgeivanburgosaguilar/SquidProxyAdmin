#!/usr/bin/env python
'''
Obtener Asignaciones para DHCP
Genera las asignaciones configuradas en la base de datos para DHCP (Dnsmasq)
'''
import django
import os
import sys
from configparser import ConfigParser
from funciones import obtener_ruta_configuraciones


# Cargar configuraciones
configParser = ConfigParser()
configParser.read(os.path.join(
  obtener_ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
en_produccion = configParser.getboolean('FiltroWeb', 'Produccion')

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

from Administrador.models import Asignacion

try:
  asignaciones = Asignacion.objects.all().values('ip', 'mac')
  for asignacion in asignaciones:
    sys.stdout.write(
      f'dhcp-host={asignacion["mac"].upper()},192.168.2.{asignacion["ip"]}\n')
except Exception as e:
  if not en_produccion:
    sys.stdout.write(f'{str(type(e))}: {str(e)}')
