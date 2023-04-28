#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Filtrado Web por la Extension del archivo 1.5
# ACL Externa para Squid 3.5
import os
import sys
import re
from urlparse import urlparse
from urllib import quote, unquote_plus
from ConfigParser import SafeConfigParser
from Funciones import obtener_ruta_configuraciones, es_una_ipv4_valida, squid_mensaje


# Cargar configuraciones
configParser = SafeConfigParser()
configParser.read(os.path.join(obtener_ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
en_produccion = configParser.getboolean('FiltroWeb', 'Produccion')

# Mensajes de Error
ArgsError = quote(configParser.get('Mensajes', 'ArgsError'))
ArgsPathError = quote(configParser.get('Mensajes', 'ArgsPathError'))
IPError = quote(configParser.get('Mensajes', 'IPError'))
IPSinAsignacion = quote(configParser.get('Mensajes', 'IPSinAsignacion'))
AccesoDenegadoExtensionArchivo = quote(configParser.get('Mensajes', 'AccesoDenegadoExtensionArchivo'))
AccesoDenegadoSinAccesoAInternet = quote(configParser.get('Mensajes', 'AccesoDenegadoSinAccesoAInternet'))
EnMantenimiento = quote(configParser.get('Mensajes', 'EnMantenimiento'))
MuerteSubita = quote(configParser.get('Mensajes', 'MuerteSubita'))


# Cargar backend basado en Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SquidProxyAdmin.settings')
django.setup()

# Importes de Django
from django.db import close_old_connections, ProgrammingError, OperationalError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from Administrador.models import Asignacion, ExtensionArchivo, Configuracion


# Variables
FIN = False
RecienNacido = True
regexp_ip = re.compile(r"\A([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$")
ips_localhost = ['127.0.0.1', '::', '::1']

# El Ciclo de la vida
try:
    while not FIN:
        # Vaciamos la salida al comenzar
        if RecienNacido:
            RecienNacido = False
        else:
            sys.stdout.flush()

        # Estructura de Argumentos: <IP> <URL PATH>
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
        url_path = unquote_plus(argumentos[1]).lower()

        # Verifica que la ruta de la url no sea invalida
        if not url_path:
            squid_mensaje(mensaje=ArgsPathError)
            continue

        # Si la IP del cliente corresponde a una ip conocida de localhost entonces lo dejamos de procesar
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
        except (ObjectDoesNotExist):
            # IP sin Asignacion
            squid_mensaje(mensaje=IPSinAsignacion)
            continue

        except (MultipleObjectsReturned, ValueError, IndexError, AttributeError, re.error):
            # Error al procesar la IP del cliente
            squid_mensaje(mensaje=IPError)
            continue

        # Cache del nivel
        nivel = asignacion.nivel

        # Si el nivel de la asignacion no se debe filtrar, entonces dejalo pasar (Nivel: Sin Filtro)
        if not nivel.filtrar:
            squid_mensaje('ERR')
            continue

        # Si el nivel no tiene acceso a internet entonces le denegamos el acceso a todos los recursos de internet (Ejemplo: Nivel Sin Acceso a Internet)
        if nivel.sinaccesoainternet:
            squid_mensaje(mensaje=AccesoDenegadoSinAccesoAInternet)
            continue

        # Completo el path para que se vuelva una URI y lo pueda procesar
        # con la libreria estandar urlparse, con la cual puedo obtener
        # solamente la ruta de la URI sin el query string de una URL,
        # ya que squid nos envia el path junto con la query string
        url_path_extension = ''
        try:
            path = urlparse('http://localhost/{0}'.format(url_path)).path
            url_path_extension = os.path.splitext(path)[1]
        except:
            url_path_extension = ''

        # Si tiene una extension entonces comprobamos si no esta permitida para el nivel de la asignacion
        if url_path_extension:
            # Obtener el estatus del modo de actualizacion (siempre y cuando el nivel pueda entrar en modo de actualizacion)
            permitir_actualizaciones = False
            if nivel.actualizaciones:
                try:
                    if Configuracion.objects.filter(nombre__exact='PermitirActualizaciones', valor__exact='1').order_by().exists():
                        permitir_actualizaciones = True

                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    permitir_actualizaciones = False


            # Comprobar si la extension de archivo no esta en la lista negra del nivel (excluyendo o no los que se aceptan al permitir actualizaciones).
            NoPermitirExtensionArchivo = False
            if permitir_actualizaciones:
                NoPermitirExtensionArchivo = ExtensionArchivo.objects.filter(nivel__id__exact=nivel.id).exclude(actualizaciones__exact=True).extra(where=['%s LIKE extension'], params=[url_path_extension]).order_by().exists()
            else:
                NoPermitirExtensionArchivo = ExtensionArchivo.objects.filter(nivel__id__exact=nivel.id).extra(where=['%s LIKE extension'], params=[url_path_extension]).order_by().exists()

            if NoPermitirExtensionArchivo:
                squid_mensaje(mensaje=AccesoDenegadoExtensionArchivo)
                continue

        # Probablemente la extension del archivo sea benigna
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
        sys.stdout.write('{0}: {1}'.format(str(type(e)), str(e)))

    squid_mensaje(mensaje='Error', registro='ErrorExternalACL-ExtensionArchivo')