#!/usr/bin/env python
'''
Obtiene las asignaciones de la base de datos para el servidor DHCP (Dnsmasq)
'''
import os
import sys
import django
from funciones import estamos_en_produccion

# Agregar directorio actual a las rutas del entorno
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importar modelos
from Administrador.models import Asignacion

# Configuraciones
PRODUCCION = estamos_en_produccion()

try:
  asignaciones = Asignacion.objects.all().values('ip', 'mac')
  for asignacion in asignaciones:
    sys.stdout.write(
      f'dhcp-host={asignacion["mac"].upper()},192.168.2.{asignacion["ip"]}\n')
except Exception as e:
  if not PRODUCCION:
    sys.stdout.write(f'{str(type(e))}: {str(e)}')
