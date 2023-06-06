#!/usr/bin/env python
'''
Filtrado Web por Host/Dominio 3.0
ACL Externa para Squid 3.5
'''
import os
import sys
import re
import django
from django.db import close_old_connections, ProgrammingError, OperationalError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datetime import date
from urllib.parse import quote, unquote_plus
from funciones import (estamos_en_produccion, procesar_tlds,
                       es_una_ipv4_valida, obtener_dominio, squid_mensaje)


# Agregar directorio actual a las rutas del entorno
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar backend basado en Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importar modelos
from Administrador.models import (Asignacion, SitioPermanentementePermitido,
                                  SitioPermanentementeDenegado,
                                  AsignacionTemporalUsuario,
                                  AsignacionTemporalDepartamento, Sitio)

# Configuraciones y mensajes de error
PRODUCCION = estamos_en_produccion()
ARGSERROR = quote(os.getenv('SQUIDPROXYADM_ARGSERROR'))
IPERROR = quote(os.getenv('SQUIDPROXYADM_IPERROR'))
IPSINASIGNACION = quote(os.getenv('SQUIDPROXYADM_IPSINASIGNACION'))
DOMINIOINVALIDO = quote(os.getenv('SQUIDPROXYADM_DOMINIOINVALIDO'))
ACCESODENEGADO = quote(os.getenv('SQUIDPROXYADM_ACCESODENEGADO'))
ACCESODENEGADOSINACCESOAINTERNET = quote(
  os.getenv('SQUIDPROXYADM_ACCESODENEGADOSINACCESOAINTERNET'))
ENMANTENIMIENTO = quote(os.getenv('SQUIDPROXYADM_ENMANTENIMIENTO'))
MUERTESUBITA = quote(os.getenv('SQUIDPROXYADM_MUERTESUBITA'))

# Variables
FIN = False
recien_nacido = True
regexp_ip = re.compile(
  r'\A([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$')
ips_localhost = ['127.0.0.1', '::', '::1']
TLDS = procesar_tlds()
SQUIDPASS = 'ERR'

# El Ciclo de la vida
try:
  while not FIN:
    # Vaciamos la salida al comenzar
    if recien_nacido:
      recien_nacido = False
    else:
      sys.stdout.flush()

    # Estructura de Argumentos: <IP> <Host>
    linea = sys.stdin.readline()

    # Si obtiene EOF de Squid
    if not linea:
      FIN = True
      continue

    # Sanitizacion y separacion de la linea de argumentos entregada
    argumentos = linea.strip('. \n\r').split(' ')

    # Validacion del numero de argumentos
    if len(argumentos) < 2:
      squid_mensaje(mensaje=ARGSERROR)
      continue

    # Inicializamos variables con los argumentos
    ip_cliente = unquote_plus(argumentos[0])
    host = unquote_plus(argumentos[1]).lower()

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

    # Si el host se encuentra en la lista de sitios permitidos
    if SitioPermanentementePermitido.objects.extra(where=['%s LIKE dominio'], params=[host]).order_by().exists():
      squid_mensaje(SQUIDPASS)
      continue

    # Si el host se encuentra en la lista de sitios denegados
    if SitioPermanentementeDenegado.objects.extra(where=['%s LIKE dominio'], params=[host]).order_by().exists():
      squid_mensaje(mensaje=SQUIDPASS)
      continue

    # Cache del usuario
    usuario = asignacion.usuario
    departamento = usuario.departamento
    fecha_hoy = date.today()

    # Si el departamento tiene asignaciones/permisos temporales
    if AsignacionTemporalDepartamento.objects.extra(where=['%s LIKE dominio'], params=[host]).filter(departamento__id__exact=departamento.id, fecha_expiracion__gte=fecha_hoy).order_by().exists():
      squid_mensaje(SQUIDPASS)
      continue

    # Si el usuario tiene asignaciones/permisos temporales
    if AsignacionTemporalUsuario.objects.extra(where=['%s LIKE dominio'], params=[host]).filter(usuario__id__exact=usuario.id, fecha_expiracion__gte=fecha_hoy).order_by().exists():
      squid_mensaje(SQUIDPASS)
      continue

    # Extraemos el dominio efectivo
    try:
      host_efectivo = obtener_dominio(host, TLDS, True)
    except ValueError:
      squid_mensaje(mensaje=DOMINIOINVALIDO)
      continue

    # Si el host efectivo se encuentra en la lista de sitios
    if Sitio.objects.filter(categoria__nivel__id__exact=nivel.id, dominio__exact=host_efectivo).order_by().exists():
      if nivel.lista_blanca:
        squid_mensaje(SQUIDPASS)
        continue
      else:
        squid_mensaje(mensaje=ACCESODENEGADO)
        continue

    # Si el host es el efectivo pero con www,
    # entonces tratalo como el dominio efectivo
    if host == f'www.{host_efectivo}':
      host = host_efectivo

    # Si el host completo no es el mismo que el efectivo
    if host != host_efectivo:
      if Sitio.objects.filter(categoria__nivel__id__exact=nivel.id, dominio__exact=host).order_by().exists():
        if nivel.lista_blanca:
          squid_mensaje(SQUIDPASS)
          continue
        else:
          squid_mensaje(mensaje=ACCESODENEGADO)
          continue

    # No encontramos el registro en las lista bloqueo probablemente sea benigno
    if nivel.lista_blanca:
      squid_mensaje(mensaje=ACCESODENEGADO)
    else:
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

  squid_mensaje(mensaje='Error', registro='ErrorExternalACL-Dominio')
