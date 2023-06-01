#!/usr/bin/env python
'''
Filtrado Web por MIME 1.5
ACL Externa para Squid 3.5
'''
import os
import sys
import re
import django
from urllib.parse import quote, unquote_plus
from configparser import ConfigParser
from funciones import ruta_configuraciones, es_una_ipv4_valida, squid_mensaje


# Cargar configuraciones
config_parser = ConfigParser()
config_parser.read(os.path.join(
  ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
en_produccion = config_parser.getboolean('FiltroWeb', 'Produccion')
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Mensajes de Error
ArgsError = quote(config_parser.get('Mensajes', 'ArgsError'))
IPError = quote(config_parser.get('Mensajes', 'IPError'))
IPSinAsignacion = quote(config_parser.get('Mensajes', 'IPSinAsignacion'))
AccesoDenegadoTipoArchivo = quote(
  config_parser.get('Mensajes', 'AccesoDenegadoTipoArchivo'))
AccesoDenegadoSinAccesoAInternet = quote(
  config_parser.get('Mensajes', 'AccesoDenegadoSinAccesoAInternet'))
EnMantenimiento = quote(config_parser.get('Mensajes', 'EnMantenimiento'))
MuerteSubita = quote(config_parser.get('Mensajes', 'MuerteSubita'))

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importes de Django
# pylint: disable=wrong-import-position
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import close_old_connections, ProgrammingError, OperationalError
from Administrador.models import Asignacion, TipoMime, Configuracion
# pylint: enable=wrong-import-position


# Variables
FIN = False
recien_nacido = True
regexp_ip = re.compile(
  r'\A([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$')
regexp_mime = re.compile(r'([\w\-./+]+);?.*')
ips_localhost = ['127.0.0.1', '::', '::1']

# El Ciclo de la vida
try:
  while not FIN:
    # Vaciamos la salida al comenzar
    if recien_nacido:
      recien_nacido = False
    else:
      sys.stdout.flush()

    # Estructura de Argumentos: <IP> <CONTENT-TYPE HTTP HEADER>
    linea = sys.stdin.readline()

    # Si obtiene EOF de Squid
    if not linea:
      FIN = True
      continue

    # Sanitizacion y separacion de la linea de argumentos entregada
    argumentos = linea.strip('. \n\r').split(' ')

    # Validacion del numero de argumentos
    if len(argumentos) < 2:
      squid_mensaje(mensaje=ArgsError)
      continue

    # Inicializamos variables con los argumentos
    ip_cliente = unquote_plus(argumentos[0])
    tipo_mime = unquote_plus(argumentos[1]).lower()

    # Si la IP del cliente corresponde a una ip de localhost
    if ip_cliente in ips_localhost:
      squid_mensaje('ERR')
      continue

    # Variables de sesion
    asignacion = {}
    nivel = {}

    # Obtenemos la informacion de la asignacion
    try:
      # Validacion de la IP
      if not es_una_ipv4_valida(ip_cliente):
        raise ValueError

      octetos_ip_cliente = regexp_ip.search(ip_cliente)
      ip_cliente_octeto4 = int(octetos_ip_cliente.group(4))
      asignacion = Asignacion.objects.get(ip__exact=ip_cliente_octeto4)
    except ObjectDoesNotExist:
      squid_mensaje(mensaje=IPSinAsignacion)
      continue

    except (MultipleObjectsReturned, ValueError, IndexError, AttributeError, re.error):
      squid_mensaje(mensaje=IPError)
      continue

    # Cache del nivel
    nivel = asignacion.nivel

    # Si el nivel no se debe filtrar
    if not nivel.filtrar:
      squid_mensaje('ERR')
      continue

    # Si el nivel no tiene acceso a internet
    if nivel.sinaccesoainternet:
      squid_mensaje(mensaje=AccesoDenegadoSinAccesoAInternet)
      continue

    # Obtenemos el Tipo MIME
    try:
      mime = regexp_mime.search(tipo_mime)
      tipo_mime = mime.group(1)
    except:
      tipo_mime = ''

    # Si tiene un tipo mime entonces comprobamos si no esta permitido para el nivel de la asignacion
    if tipo_mime:
      # Obtener el estatus del modo de actualizacion (siempre y cuando el nivel pueda entrar en modo de actualizacion)
      permitir_actualizaciones = False
      if nivel.actualizaciones:
        try:
          if Configuracion.objects.filter(nombre__exact='PermitirActualizaciones', valor__exact='1').order_by().exists():
            permitir_actualizaciones = True

        except (ObjectDoesNotExist, MultipleObjectsReturned):
          permitir_actualizaciones = False

      # Comprobar si el tipo de mime no esta en la lista negra del nivel (excluyendo o no los que se aceptan al permitir actualizaciones).
      NoPermitirMime = False
      if permitir_actualizaciones:
        NoPermitirMime = TipoMime.objects.filter(nivel__id__exact=nivel.id).exclude(
          actualizaciones__exact=True).extra(where=['%s LIKE mime'], params=[tipo_mime]).order_by().exists()
      else:
        NoPermitirMime = TipoMime.objects.filter(nivel__id__exact=nivel.id).extra(
          where=['%s LIKE mime'], params=[tipo_mime]).order_by().exists()

      if NoPermitirMime:
        squid_mensaje(mensaje=AccesoDenegadoTipoArchivo)
        continue

    # Probablemente el tipo mime sea benigno
    squid_mensaje('ERR')

  else:
    close_old_connections()

except ProgrammingError:
  squid_mensaje(mensaje=EnMantenimiento, registro='EnMantenimiento')

except OperationalError:
  squid_mensaje(mensaje=MuerteSubita, registro='MuerteSubita')

except EOFError:
  squid_mensaje(mensaje='EOF', registro='EOF')

except KeyboardInterrupt:
  squid_mensaje(mensaje='Interrupcion_del_Teclado', registro='KBI')

except Exception as e:
  if not en_produccion:
    sys.stdout.write(f'{str(type(e))}: {str(e)}')

  squid_mensaje(mensaje='Error', registro='ErrorExternalACL-MIME')
