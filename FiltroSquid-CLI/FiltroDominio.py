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
from configparser import ConfigParser
from funciones import (obtener_ruta_configuraciones, es_una_ipv4_valida,
                       obtener_dominio, squid_mensaje)


# Agregar directorio actual a las rutas del entorno
current_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_path)

# Cargar configuraciones
config_parser = ConfigParser()
config_parser.read(os.path.join(
  obtener_ruta_configuraciones(), 'principal.conf'))

# Directivas y mensajes de error
en_produccion = config_parser.getboolean('FiltroWeb', 'Produccion')
ArgsError = quote(config_parser.get('Mensajes', 'ArgsError'))
IPError = quote(config_parser.get('Mensajes', 'IPError'))
IPSinAsignacion = quote(config_parser.get('Mensajes', 'IPSinAsignacion'))
DominioInvalido = quote(config_parser.get('Mensajes', 'DominioInvalido'))
AccesoDenegado = quote(config_parser.get('Mensajes', 'AccesoDenegado'))
AccesoDenegadoSinAccesoAInternet = quote(
  config_parser.get('Mensajes', 'AccesoDenegadoSinAccesoAInternet'))
EnMantenimiento = quote(config_parser.get('Mensajes', 'EnMantenimiento'))
MuerteSubita = quote(config_parser.get('Mensajes', 'MuerteSubita'))

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importar modelos
from Administrador.models import (Asignacion, SitioPermanentementePermitido,
                                  SitioPermanentementeDenegado,
                                  AsignacionTemporalUsuario,
                                  AsignacionTemporalDepartamento, Sitio)


# Variables
FIN = False
recien_nacido = True
regexp_ip = re.compile(
  r'\A([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$')
ips_localhost = ['127.0.0.1', '::', '::1']

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
      squid_mensaje(mensaje=ArgsError)
      continue

    # Inicializamos variables con los argumentos
    ip_cliente = unquote_plus(argumentos[0])
    host = unquote_plus(argumentos[1]).lower()

    # Si la IP es localhost lo dejamos pasar
    if ip_cliente in ips_localhost:
      squid_mensaje('ERR')
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
      squid_mensaje(mensaje=IPSinAsignacion)
      continue

    except (MultipleObjectsReturned, ValueError, IndexError, re.error):
      squid_mensaje(mensaje=IPError)
      continue

    # Cache del nivel
    nivel = asignacion.nivel

    # Si el nivel de la asignacion no se debe filtrar
    if not nivel.filtrar:
      squid_mensaje('ERR')
      continue

    # Si el nivel no tiene acceso a internet
    if nivel.sinaccesoainternet:
      squid_mensaje(mensaje=AccesoDenegadoSinAccesoAInternet)
      continue

    # Si el host se encuentra en la lista de sitios permitidos
    if SitioPermanentementePermitido.objects.extra(where=['%s LIKE dominio'], params=[host]).order_by().exists():
      squid_mensaje('ERR')
      continue

    # Si el host se encuentra en la lista de sitios denegados
    if SitioPermanentementeDenegado.objects.extra(where=['%s LIKE dominio'], params=[host]).order_by().exists():
      squid_mensaje(mensaje=AccesoDenegado)
      continue

    # Cache del usuario
    usuario = asignacion.usuario
    departamento = usuario.departamento
    fecha_hoy = date.today()

    # Si el departamento tiene asignaciones/permisos temporales
    if AsignacionTemporalDepartamento.objects.extra(where=['%s LIKE dominio'], params=[host]).filter(departamento__id__exact=departamento.id, fecha_expiracion__gte=fecha_hoy).order_by().exists():
      squid_mensaje('ERR')
      continue

    # Si el usuario tiene asignaciones/permisos temporales
    if AsignacionTemporalUsuario.objects.extra(where=['%s LIKE dominio'], params=[host]).filter(usuario__id__exact=usuario.id, fecha_expiracion__gte=fecha_hoy).order_by().exists():
      squid_mensaje('ERR')
      continue

    # Extraemos el dominio efectivo
    try:
      host_efectivo = obtener_dominio(host, True)
    except ValueError:
      squid_mensaje(mensaje=DominioInvalido)
      continue

    # Si el host efectivo se encuentra en la lista de sitios
    if Sitio.objects.filter(categoria__nivel__id__exact=nivel.id, dominio__exact=host_efectivo).order_by().exists():
      if nivel.lista_blanca:
        squid_mensaje('ERR')
        continue
      else:
        squid_mensaje(mensaje=AccesoDenegado)
        continue

    # Si el host es el efectivo pero con www,
    # entonces tratalo como el dominio efectivo
    if host == f'www.{host_efectivo}':
      host = host_efectivo

    # Si el host completo no es el mismo que el efectivo
    if host != host_efectivo:
      if Sitio.objects.filter(categoria__nivel__id__exact=nivel.id, dominio__exact=host).order_by().exists():
        if nivel.lista_blanca:
          squid_mensaje('ERR')
          continue
        else:
          squid_mensaje(mensaje=AccesoDenegado)
          continue

    # No encontramos el registro en las listas negras probablemente sea benigno
    if nivel.lista_blanca:
      squid_mensaje(mensaje=AccesoDenegado)
    else:
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
  squid_mensaje(mensaje='KBI', registro='KBI')

except Exception as e:
  if not en_produccion:
    sys.stdout.write(f'{str(type(e))}: {str(e)}')

  squid_mensaje(mensaje='Error', registro='ErrorExternalACL-Dominio')
