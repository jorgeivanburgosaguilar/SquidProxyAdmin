#!/usr/bin/env python
'''
Filtrado Web por MIME 1.5
ACL Externa para Squid 3.5
'''
import os
import sys
import re
import django
from django.db import close_old_connections, ProgrammingError, OperationalError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from urllib.parse import quote, unquote_plus
from funciones import estamos_en_produccion, es_una_ipv4_valida, squid_mensaje


# Agregar directorio actual a las rutas del entorno
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importar modelos
from Administrador.models import Asignacion, TipoMime, Configuracion

# Configuraciones y mensajes de error
PRODUCCION = estamos_en_produccion()
ARGSERROR = quote(os.getenv('SQUIDPROXYADM_ARGSERROR'))
IPERROR = quote(os.getenv('SQUIDPROXYADM_IPERROR'))
IPSINASIGNACION = quote(os.getenv('SQUIDPROXYADM_IPSINASIGNACION'))
ACCESODENEGADOTIPOARCHIVO = quote(
  os.getenv('SQUIDPROXYADM_ACCESODENEGADOTIPOARCHIVO'))
ACCESODENEGADOSINACCESOAINTERNET = quote(
  os.getenv('SQUIDPROXYADM_ACCESODENEGADOSINACCESOAINTERNET'))
ENMANTENIMIENTO = quote(os.getenv('SQUIDPROXYADM_ENMANTENIMIENTO'))
MUERTESUBITA = quote(os.getenv('SQUIDPROXYADM_MUERTESUBITA'))

# Variables
fin = False
recien_nacido = True
regexp_ip = re.compile(
  r'\A([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$')
regexp_mime = re.compile(r'([\w\-./+]+);?.*')
ips_localhost = ['127.0.0.1', '::', '::1']
SQUIDPASS = 'ERR'

try:
  while not fin:
    # Vaciamos la salida al comenzar
    if recien_nacido:
      recien_nacido = False
    else:
      sys.stdout.flush()

    # Estructura de Argumentos: <IP> <CONTENT-TYPE HTTP HEADER>
    linea = sys.stdin.readline()

    # Si obtiene EOF de Squid
    if not linea:
      fin = True
      continue

    # Sanitizacion y separacion de la linea de argumentos entregada
    argumentos = linea.strip('. \n\r').split(' ')

    # Validacion del numero de argumentos
    if len(argumentos) < 2:
      squid_mensaje(mensaje=ARGSERROR)
      continue

    # Inicializacion
    ip_cliente = unquote_plus(argumentos[0])
    tipo_mime = unquote_plus(argumentos[1]).lower()

    # Si la IP es localhost lo dejamos pasar
    if ip_cliente in ips_localhost:
      squid_mensaje(SQUIDPASS)
      continue

    # Cache de la asignacion
    asignacion: Asignacion = None

    # Obtenemos la informacion de la asignacion
    try:
      if not es_una_ipv4_valida(ip_cliente):
        raise ValueError

      octetos_ip_cliente = regexp_ip.search(ip_cliente)
      ip_cliente_octeto4 = int(octetos_ip_cliente.group(4))
      asignacion = Asignacion.objects.get(ip__exact=ip_cliente_octeto4)
    except ObjectDoesNotExist:
      squid_mensaje(mensaje=IPSINASIGNACION)
      continue

    except (MultipleObjectsReturned, ValueError, IndexError
            ,re.error, AttributeError):
      squid_mensaje(mensaje=IPERROR)
      continue

    # Cache del nivel
    nivel = asignacion.nivel

    # Si el nivel de la asignacion no se debe filtrar
    if not nivel.filtrar:
      squid_mensaje(SQUIDPASS)
      continue

    # Si el nivel no tiene acceso a internet
    if nivel.sinaccesoainternet:
      squid_mensaje(mensaje=ACCESODENEGADOSINACCESOAINTERNET)
      continue

    # Obtenemos el Tipo MIME
    try:
      mime = regexp_mime.search(tipo_mime)
      tipo_mime = mime.group(1)
    except (ValueError, IndexError, re.error):
      tipo_mime = ''

    # Si tiene un tipo mime entonces comprobamos si no
    # esta permitido para el nivel de la asignacion
    if tipo_mime:
      # Obtener el estatus del modo de actualizacion,
      # siempre y cuando el nivel pueda entrar en modo de actualizacion
      permitir_actualizaciones = False
      if nivel.actualizaciones:
        try:
          if Configuracion.objects.filter(nombre__exact='PermitirActualizaciones', valor__exact='1').order_by().exists():
            permitir_actualizaciones = True

        except (ObjectDoesNotExist, MultipleObjectsReturned):
          permitir_actualizaciones = False

      # Comprobar si el tipo de mime no esta en la lista de bloqueo del nivel
      # excluyendo o no los que se aceptan al permitir actualizaciones.
      no_permitir_mime = False
      if permitir_actualizaciones:
        no_permitir_mime = TipoMime.objects.filter(nivel__id__exact=nivel.id).exclude(
          actualizaciones__exact=True).extra(where=['%s LIKE mime'], params=[tipo_mime]).order_by().exists()
      else:
        no_permitir_mime = TipoMime.objects.filter(nivel__id__exact=nivel.id).extra(
          where=['%s LIKE mime'], params=[tipo_mime]).order_by().exists()

      if no_permitir_mime:
        squid_mensaje(mensaje=ACCESODENEGADOTIPOARCHIVO)
        continue

    # Probablemente el tipo mime sea benigno
    squid_mensaje(SQUIDPASS)

  else:
    close_old_connections()

except ProgrammingError:
  squid_mensaje(mensaje=ENMANTENIMIENTO, registro='EnMantenimiento')

except OperationalError:
  squid_mensaje(mensaje=MUERTESUBITA, registro='MuerteSubita')

except EOFError:
  squid_mensaje(mensaje='EOF', registro='EOF')

except KeyboardInterrupt:
  squid_mensaje(mensaje='KBI', registro='KBI')

except Exception as e:
  if not PRODUCCION:
    sys.stdout.write(f'{str(type(e))}: {str(e)}')

  squid_mensaje(mensaje='Error', registro='ErrorExternalACL-MIME')
