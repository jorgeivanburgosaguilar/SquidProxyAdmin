'''
Views
'''
import ipaddress
from django.http import JsonResponse
from django.shortcuts import render
from Administrador.models import Asignacion, Red


def index(request):
  asignaciones = Asignacion.objects.all().values('ip', 'mac',
                                                 'usuario__nombre',
                                                 'usuario__departamento__nombre',
                                                 'nivel__nombre',
                                                 'equipo__nombre',
                                                 'tipo_conexion',
                                                 'nombre_equipo')
  return render(request, 'Administrador/index.html', {'asignaciones': asignaciones})


def update_ip_choices(request):
  red_id = request.GET.get('red_id')
  current_value = request.GET.get('current_value')
  ip_choices = get_updated_ip_choices(red_id, current_value)
  return JsonResponse(ip_choices)


def get_updated_ip_choices(red_id, current_value):
  ip_choices = [('', '---------')]
  try:
    if not red_id:
      raise Red.DoesNotExist

    red = Red.objects.get(pk=red_id)
    network = ipaddress.ip_network(red.cidr)
    ips_asignadas = list(Asignacion.objects.values_list('ip', flat=True))

    ips_ocupadas: tuple = None
    if not red.inicio_dhcp or not red.fin_dhcp:
      ips_ocupadas = tuple(ips_asignadas)
    else:
      ips_rango_dinamico = generar_rango_ip(
        network, red.inicio_dhcp, red.fin_dhcp)
      ips_ocupadas = tuple(ips_asignadas + ips_rango_dinamico)

    for ip in network.hosts():
      ip_str = str(ip)
      if ip_str not in ips_ocupadas or ip_str == current_value:
        ip_choices.append((ip_str, ip_str))

  except (Red.DoesNotExist, ValueError):
    pass

  return {'choices': ip_choices}


def generar_rango_ip(network, inicio_dhcp, fin_dhcp):
  start_ip = ipaddress.ip_address(inicio_dhcp)
  end_ip = ipaddress.ip_address(fin_dhcp)
  return [str(ip) for ip in network if start_ip <= ip <= end_ip]
