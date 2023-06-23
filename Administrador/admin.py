'''
Admin
'''
import ipaddress
from django import forms
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from Administrador import models


@admin.register(models.Departamento)
class DepartamentoAdmin(SimpleHistoryAdmin):
  list_display = ('nombre',)
  search_fields = ['nombre']


@admin.register(models.Usuario)
class UsuarioAdmin(SimpleHistoryAdmin):
  list_display = ('nombre', 'departamento', 'activo', 'comentario')
  list_max_show_all = 400
  list_per_page = 400
  search_fields = ['nombre']


@admin.register(models.Categoria)
class CategoriaAdmin(SimpleHistoryAdmin):
  list_display = ('nombre', 'descripcion', 'ruta')


@admin.register(models.Nivel)
class NivelAdmin(SimpleHistoryAdmin):
  list_display = ('nombre', 'filtrar', 'sinaccesoainternet', 'lista_blanca')
  filter_horizontal = ('categorias', )


@admin.register(models.Sitio)
class SitioAdmin(admin.ModelAdmin):
  list_display = ('dominio', 'categoria')
  search_fields = ['dominio']


@admin.register(models.SitioPermanentementePermitido)
class SitioPermanentementePermitidoAdmin(SimpleHistoryAdmin):
  list_display = ('dominio',)
  search_fields = ['dominio']


@admin.register(models.SitioPermanentementeDenegado)
class SitioPermanentementeDenegadoAdmin(SimpleHistoryAdmin):
  list_display = ('dominio',)
  search_fields = ['dominio']


@admin.register(models.AsignacionTemporalDepartamento)
class AsignacionTemporalDepartamentoAdmin(SimpleHistoryAdmin):
  list_display = ('dominio', 'departamento',
                  'fecha_creacion', 'fecha_expiracion')
  search_fields = ['dominio']


@admin.register(models.AsignacionTemporalUsuario)
class AsignacionTemporalUsuarioAdmin(SimpleHistoryAdmin):
  list_display = ('dominio', 'usuario', 'fecha_creacion', 'fecha_expiracion')
  search_fields = ['dominio']


@admin.register(models.Equipo)
class EquipoAdmin(SimpleHistoryAdmin):
  list_display = ('nombre',)
  list_max_show_all = 400
  list_per_page = 400
  search_fields = ['nombre']


class AsignacionAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['usuario'].queryset = models.Usuario.objects.filter(
      activo__exact=True)
    ip_choices = self.obtener_ips_disponibles()
    self.fields['ip'].widget = forms.Select(choices=ip_choices)

  def obtener_ips_disponibles(self):
    'Obtiene las IPs que quedan disponibles incluyendo la de la instancia actual.'
    ips_asignadas = tuple(
      models.Asignacion.objects.values_list('ip', flat=True))
    # ips_rango_dinamico = list(range(195, 200))
    # ips_ocupadas = ips_asignadas + ips_rango_dinamico
    # ips_disponibles = []
    # ips_disponibles.append(('', '---------'))

    ip_list = [('', '---------')]
    network = ipaddress.ip_network('192.168.2.0/24')
    for ip in network.hosts():
      ip_str = str(ip)
      if ip_str not in ips_asignadas or ip_str == self.instance.ip:
        ip_list.append((ip_str, ip_str))

    return tuple(ip_list)


@admin.register(models.Asignacion)
class AsignacionAdmin(SimpleHistoryAdmin):
  list_display = ('ip', 'mac', 'nombre_equipo', 'usuario',
                  'obtener_departamento_usuario', 'nivel', 'equipo',
                  'tipo_conexion', 'ultima_actualizacion')
  list_max_show_all = 255
  list_per_page = 255
  form = AsignacionAdminForm


admin.site.site_header = 'Administración del Proxy'
admin.site.site_title = 'Administración del Proxy'
admin.site.index_title = 'Administración'
