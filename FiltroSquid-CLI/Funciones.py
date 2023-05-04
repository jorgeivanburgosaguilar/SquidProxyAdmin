#!/usr/bin/env python
''' funciones comunes '''
import os
import sys
import socket
from urllib.parse import urlparse


def obtener_ruta_configuraciones():
  current_directory = os.path.dirname(os.path.realpath(__file__))
  return os.path.abspath(os.path.join(current_directory, 'Configuraciones'))


def obtener_ruta_tlds():
  return os.path.join(obtener_ruta_configuraciones(), 'effective_tld_names.dat')


# TLDs Globales Validos
with open(obtener_ruta_tlds(), 'r', encoding='utf-8') as archivo:
  tlds = [linea.strip() for linea in archivo if linea[0] not in '/\n']


def squid_mensaje(tipo='OK', mensaje='', registro=''):
  '''Imprime una mensaje con el formato para los ACL Externos de Squid 3.x '''
  if mensaje:
    mensaje = f' message={mensaje}'

  if registro:
    registro = f' log={registro}'

  sys.stdout.write(f'{tipo.upper()}{mensaje}{registro}\n')


def es_una_ipv4_valida(ip):
  '''Funcion para validar una IPv4'''
  try:
    socket.inet_aton(ip)
    return True
  except socket.error:
    return None


def es_un_dominio_valido(dominio):
  '''Funcion para verificar que el dominio sea valido'''
  dominio = f'http://{dominio}/'

  # Obten el Host de la URI
  urlElements = urlparse(dominio)[1]

  # Si el host es una direccion IPv4 entonces es un dominio valido
  if (es_una_ipv4_valida(urlElements)):
    return True

  urlElements = urlElements.lower().split('.')
  for i in range(-len(urlElements), 0):
    lastIElements = urlElements[i:]

    candidate = '.'.join(lastIElements)
    wildcardCandidate = '.'.join(['*'] + lastIElements[1:])
    exceptionCandidate = '!' + candidate

    if (exceptionCandidate in tlds):
      return True

    if (candidate in tlds or wildcardCandidate in tlds):
      return True

  return None


def obtener_dominio(dominio, efectivo=False):
  '''Funcion para obtener el host/dominio de una URL'''
  dominio = 'http://{0}/'.format(dominio)

  # Obten el Host de la URI
  urlElements = urlparse(dominio)[1]

  # Si no estamos buscando el host efectivo devuelvelo asi como esta
  if not efectivo:
    return urlElements.lower()

  # Si el host es una direccion IPv4 entonces deja de procesar y devuelve la
  # direccion como host
  if (es_una_ipv4_valida(urlElements)):
    return urlElements

  urlElements = urlElements.lower().split('.')
  for i in range(-len(urlElements), 0):
    lastIElements = urlElements[i:]

    candidate = '.'.join(lastIElements)
    wildcardCandidate = '.'.join(['*'] + lastIElements[1:])
    exceptionCandidate = '!' + candidate

    if exceptionCandidate in tlds:
      return '.'.join(urlElements[i:])

    if (candidate in tlds or wildcardCandidate in tlds):
      return '.'.join(urlElements[i - 1:])

  raise ValueError('Dominio Invalido')


def depurar_dominios(texto):
  '''
  Funcion para ordenar y eliminar dominios invalidos asi como duplicados
  de un cadena separada por retornos de linea.
  Devuelve una lista/coleccion
  '''
  registros_unicos = []
  lista = texto.split('\n')

  for registro in lista:
    registro = registro.rstrip('. "\'\r\t').lstrip().lower()

    if (len(registro) > 2 and es_un_dominio_valido(registro)):
      registros_unicos.append(registro)

  return registros_unicos
