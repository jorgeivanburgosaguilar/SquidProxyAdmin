'''
Admin
'''
import os
import ipaddress
from django import forms
from django.contrib import admin
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from django.forms.widgets import Select, TextInput
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


class IPFieldWidget(forms.MultiWidget):
  def __init__(self, choices=None, attrs=None):
    choices = [('---------', '---------')] + choices
    widgets = [
        Select(choices=choices),
        TextInput(attrs=attrs)
    ]
    super().__init__(widgets, attrs)

  def decompress(self, value):
    if value:
      return [value, value]
    return ['---------', '---------']


class IPField(forms.MultiValueField):
  def __init__(self, *args, **kwargs):
    fields = (
        forms.CharField(max_length=45),
        forms.CharField(max_length=45, validators=[validate_ipv46_address])
    )
    choices = kwargs.pop('choices', None)
    widget = IPFieldWidget(choices=choices, attrs=kwargs.pop('attrs', None))
    super().__init__(fields=fields, widget=widget, *args, **kwargs)

  def compress(self, data_list):
    if data_list[0] == '---------':
      if data_list[1]:
        try:
          ipaddress.ip_address(data_list[1])
        except ValueError as exc:
          raise ValidationError('Please enter a valid IP address.') from exc
        return data_list[1]
      return None
    if data_list[0]:
      return data_list[0]
    return ''

  def validate(self, value):
    super().validate(value)
    if value[0] == '---------' and not value[1]:
      raise ValidationError('Please enter a valid IP address.')


class AsignacionAdminForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['usuario'].queryset = models.Usuario.objects.filter(
      activo__exact=True)
    es_ipv6 = os.getenv('SQUIDPROXYADM_ESIPV6', 'False') == 'True'
    iprange = os.getenv('SQUIDPROXYADM_IPRANGE')
    available_ips: list[tuple[str, str]] = None
    if (es_ipv6):
      available_ips = [
        (str(ip), str(ip))
        for ip in ipaddress.IPv6Network(iprange).hosts()
      ]
    else:
      available_ips = [
          (str(ip), str(ip))
          for ip in ipaddress.IPv4Network(iprange).hosts()
      ]
    self.fields['ip'] = IPField(choices=available_ips,
                                validators=[validate_ipv46_address], label='IP')


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
