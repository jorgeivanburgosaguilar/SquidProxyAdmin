#!/usr/bin/env python
'''
Obtener Asignaciones para DHCP
Genera las asignaciones configuradas en la base de datos para DHCP (Dnsmasq)
'''
import os
import sys
import django
from configparser import ConfigParser
from funciones import ruta_configuraciones

# Cargar configuraciones
config_parser = ConfigParser()
config_parser.read(os.path.join(
  ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
en_produccion = config_parser.getboolean('FiltroWeb', 'Produccion')
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# pylint: disable=wrong-import-position
from Administrador.models import Asignacion
# pylint: enable=wrong-import-position

# pylint: disable=broad-exception-caught
try:
  asignaciones = Asignacion.objects.all().values('ip', 'mac')
  for asignacion in asignaciones:
    sys.stdout.write(
      f'dhcp-host={asignacion["mac"].upper()},192.168.2.{asignacion["ip"]}\n')
except Exception as e:
  if not en_produccion:
    sys.stdout.write(f'{str(type(e))}: {str(e)}')

# pylint: enable=broad-exception-caught
