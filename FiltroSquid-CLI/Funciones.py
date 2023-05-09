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
  url_elements = urlparse(dominio)[1]

  # Si el host es una direccion IPv4 entonces es un dominio valido
  if es_una_ipv4_valida(url_elements):
    return True

  url_elements = url_elements.lower().split('.')
  for i in range(-len(url_elements), 0):
    last_ielements = url_elements[i:]

    candidate = '.'.join(last_ielements)
    wildcard_candidate = '.'.join(['*'] + last_ielements[1:])
    exception_candidate = '!' + candidate

    if exception_candidate in tlds:
      return True

    if (candidate in tlds or wildcard_candidate in tlds):
      return True

  return None


def obtener_dominio(dominio, efectivo=False):
  '''Funcion para obtener el host/dominio de una URL'''
  dominio = f'http://{dominio}/'

  # Obten el Host de la URI
  url_elements = urlparse(dominio)[1]

  # Si no estamos buscando el host efectivo devuelvelo asi como esta
  if not efectivo:
    return url_elements.lower()

  # Si el host es una direccion IPv4 entonces deja de
  # procesar y devuelve la direccion como host
  if es_una_ipv4_valida(url_elements):
    return url_elements

  url_elements = url_elements.lower().split('.')
  for i in range(-len(url_elements), 0):
    last_ielements = url_elements[i:]

    candidate = '.'.join(last_ielements)
    wildcard_candidate = '.'.join(['*'] + last_ielements[1:])
    exception_candidate = '!' + candidate

    if exception_candidate in tlds:
      return '.'.join(url_elements[i:])

    if (candidate in tlds or wildcard_candidate in tlds):
      return '.'.join(url_elements[i - 1:])

  raise ValueError('Dominio Invalido')


def depurar_dominios(texto):
  '''
  Funcion para ordenar y eliminar dominios invalidos
  asi como duplicados de un cadena separada
  por retornos de linea.
  Devuelve una lista/coleccion
  '''
  registros_unicos = []
  lista = texto.split('\n')

  for registro in lista:
    registro = registro.rstrip('. "\'\r\t').lstrip().lower()

    if (len(registro) > 2 and es_un_dominio_valido(registro)):
      registros_unicos.append(registro)

  return registros_unicos
