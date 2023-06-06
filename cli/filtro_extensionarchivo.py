#!/usr/bin/env python
'''
Filtrado Web por la Extension del archivo 1.5
ACL Externa para Squid 3.5
'''
import os
import sys
import re
import django
from django.db import close_old_connections, ProgrammingError, OperationalError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from urllib.parse import quote, unquote_plus, urlparse
from funciones import estamos_en_produccion, es_una_ipv4_valida, squid_mensaje


# Agregar directorio actual a las rutas del entorno
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importar modelos
from Administrador.models import Asignacion, ExtensionArchivo, Configuracion

# Configuraciones y mensajes de error
PRODUCCION = estamos_en_produccion()
ARGSERROR = quote(os.getenv('SQUIDPROXYADM_ARGSERROR'))
ARGSPATHERROR = quote(os.getenv('SQUIDPROXYADM_ARGSPATHERROR'))
IPERROR = quote(os.getenv('SQUIDPROXYADM_IPERROR'))
IPSINASIGNACION = quote(os.getenv('SQUIDPROXYADM_IPSINASIGNACION'))
ACCESODENEGADOEXTENSIONARCHIVO = quote(
  os.getenv('SQUIDPROXYADM_ACCESODENEGADOEXTENSIONARCHIVO'))
ACCESODENEGADOSINACCESOAINTERNET = quote(
  os.getenv('SQUIDPROXYADM_ACCESODENEGADOSINACCESOAINTERNET'))
ENMANTENIMIENTO = quote(os.getenv('SQUIDPROXYADM_ENMANTENIMIENTO'))
MUERTESUBITA = quote(os.getenv('SQUIDPROXYADM_MUERTESUBITA'))

# Variables
fin = False
recien_nacido = True
regexp_ip = re.compile(
  r'\A([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$')
ips_localhost = ['127.0.0.1', '::', '::1']
SQUIDPASS = 'ERR'

try:
  while not fin:
    # Vaciamos la salida al comenzar
    if recien_nacido:
      recien_nacido = False
    else:
      sys.stdout.flush()

    # Estructura de Argumentos: <IP> <URL PATH>
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
    url_path = unquote_plus(argumentos[1]).lower()

    # Verifica que la ruta de la URL no sea invalida
    if not url_path:
      squid_mensaje(mensaje=ARGSPATHERROR)
      continue

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

    # Completo la ruta para que se vuelva una URL y lo pueda procesar
    # con la libreria estandar urlparse, con la cual puedo obtener
    # solamente la ruta de la URL sin el query string,
    # ya que squid nos envia el path junto con la query string
    url_path_extension = ''
    try:
      path = urlparse(f'http://localhost/{url_path}').path
      url_path_extension = os.path.splitext(path)[1]
    except (ValueError, TypeError):
      url_path_extension = ''

    # Si tiene una extension entonces comprobamos si
    # no esta permitida para el nivel de la asignacion
    if url_path_extension:
      # Obtener el estatus del modo de actualizacion
      # (siempre y cuando el nivel pueda entrar en modo de actualizacion)
      permitir_actualizaciones = False
      if nivel.actualizaciones:
        try:
          if Configuracion.objects.filter(nombre__exact='PermitirActualizaciones', valor__exact='1').order_by().exists():
            permitir_actualizaciones = True

        except (ObjectDoesNotExist, MultipleObjectsReturned):
          permitir_actualizaciones = False

      # Comprobar si la extension de archivo no esta en
      # la lista de bloqueo del nivel, excluyendo o no
      # los que si aceptan al permitir actualizaciones.
      no_permitir_extension_archivo = False
      if permitir_actualizaciones:
        no_permitir_extension_archivo = ExtensionArchivo.objects.filter(nivel__id__exact=nivel.id).exclude(
          actualizaciones__exact=True).extra(where=['%s LIKE extension'], params=[url_path_extension]).order_by().exists()
      else:
        no_permitir_extension_archivo = ExtensionArchivo.objects.filter(nivel__id__exact=nivel.id).extra(
          where=['%s LIKE extension'], params=[url_path_extension]).order_by().exists()

      if no_permitir_extension_archivo:
        squid_mensaje(mensaje=ACCESODENEGADOEXTENSIONARCHIVO)
        continue

    # Probablemente la extension del archivo sea benigna
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

  squid_mensaje(mensaje='Error', registro='ErrorExternalACL-ExtensionArchivo')
