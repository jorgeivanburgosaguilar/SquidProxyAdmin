#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Filtrado Web por Host/Dominio 3.0
# ACL Externa para Squid 3.5
import os
import sys
import re
from datetime import date
from urllib import quote, unquote_plus
from ConfigParser import SafeConfigParser
from Funciones import obtener_ruta_configuraciones, es_una_ipv4_valida, obtener_dominio, squid_mensaje


# Cargar configuraciones
configParser = SafeConfigParser()
configParser.read(os.path.join(obtener_ruta_configuraciones(), 'principal.conf'))

# Directivas del Filtro
en_produccion = configParser.getboolean('FiltroWeb', 'Produccion')

# Mensajes de Error
ArgsError = quote(configParser.get('Mensajes', 'ArgsError'))
IPError = quote(configParser.get('Mensajes', 'IPError'))
IPSinAsignacion = quote(configParser.get('Mensajes', 'IPSinAsignacion'))
DominioInvalido = quote(configParser.get('Mensajes', 'DominioInvalido'))
AccesoDenegado = quote(configParser.get('Mensajes', 'AccesoDenegado'))
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
from Administrador.models import Asignacion, SitioPermanentementePermitido, SitioPermanentementeDenegado, AsignacionTemporalUsuario, AsignacionTemporalDepartamento, Sitio


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

        # Si la IP del cliente corresponde a una ip conocida de localhost entonces lo dejamos de procesar
        if ip_cliente in ips_localhost:
            squid_mensaje('ERR')
            continue

        # Variables de sesion
        asignacion = {}
        usuario = {}
        departamento = {}
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

        # Si el nivel de la asignacion no se debe filtrar, entonces dejalo pasar (Ejemplo: Nivel Sin Filtro)
        if not nivel.filtrar:
            squid_mensaje('ERR')
            continue

        # Si el nivel no tiene acceso a internet entonces le denegamos el acceso a todos los sitios de internet (Ejemplo: Nivel Sin Acceso a Internet)
        if nivel.sinaccesoainternet:
            squid_mensaje(mensaje=AccesoDenegadoSinAccesoAInternet)
            continue

        # Si el host se encuentra en la lista blanca institucional permitele el acceso
        if SitioPermanentementePermitido.objects.extra(where=['%s LIKE dominio'], params=[host]).order_by().exists():
            squid_mensaje('ERR')
            continue

        # Si el host se encuentra en la lista negra institucional no permitir el acceso
        if SitioPermanentementeDenegado.objects.extra(where=['%s LIKE dominio'], params=[host]).order_by().exists():
            squid_mensaje(mensaje=AccesoDenegado)
            continue

        # Cache del usuario
        usuario = asignacion.usuario
        departamento = usuario.departamento

        # Si el departamento tiene asignaciones/permisos temporales
        if AsignacionTemporalDepartamento.objects.extra(where=["%s LIKE dominio"], params=[host]).filter(departamento__id__exact=departamento.id, fecha_expiracion__gte=date.today()).order_by().exists():
            squid_mensaje('ERR')
            continue

        # Si el usuario tiene asignaciones/permisos temporales
        if AsignacionTemporalUsuario.objects.extra(where=['%s LIKE dominio'], params=[host]).filter(usuario__id__exact=usuario.id, fecha_expiracion__gte=date.today()).order_by().exists():
            squid_mensaje('ERR')
            continue

        # Extraemos el dominio efectivo
        try:
            host_efectivo = obtener_dominio(host, True)
            host_efectivo_con_www = 'www.{0}'.format(host_efectivo)
        except:
            squid_mensaje(mensaje=DominioInvalido)
            continue

        # Si el host efectivo se encuentra en la lista negra, entonces denegamos el acceso
        if Sitio.objects.filter(categoria__nivel__id__exact=nivel.id, dominio__exact=host_efectivo).order_by().exists():
            if nivel.lista_blanca:
                squid_mensaje('ERR')
                continue
            else:
                squid_mensaje(mensaje=AccesoDenegado)
                continue

        # Si el host es el efectivo pero con el subdominio www, entonces tratalo como el efectivo
        if host == host_efectivo_con_www:
            host = host_efectivo

        # Buscamos el host completo en todas las listas negras del nivel
        # si y solo si el host efectivo no fue previamente encontrado
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
    squid_mensaje(mensaje='Interrupcion_del_Teclado', registro='KBI')

except Exception as e:
    if not en_produccion:
        sys.stdout.write('{0}: {1}'.format(str(type(e)), str(e)))

    squid_mensaje(mensaje='Error', registro='ErrorExternalACL-Dominio')
