# -*- coding: utf-8 -*-
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
    list_display = ('nombre', 'descripcion', 'ruta', 'interna')


@admin.register(models.TipoMime)
class TipoMimeAdmin(SimpleHistoryAdmin):
    list_display = ('mime', 'actualizaciones')


@admin.register(models.ExtensionArchivo)
class ExtensionArchivoAdmin(SimpleHistoryAdmin):
    list_display = ('extension', 'actualizaciones')


@admin.register(models.Nivel)
class NivelAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'filtrar', 'sinaccesoainternet', 'actualizaciones', 'lista_blanca')
    filter_horizontal = ('categorias', 'tipos_mime', 'extensiones_archivos')


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
    list_display = ('dominio', 'departamento', 'fecha_creacion', 'fecha_expiracion')
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
        super(AsignacionAdminForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].queryset = models.Usuario.objects.filter(activo__exact=True)
        self.fields['ip'].choices = self.instance.obtener_ips_disponibles(para_admin=True)


@admin.register(models.Asignacion)
class AsignacionAdmin(SimpleHistoryAdmin):
    list_display = ('obtener_ip', 'mac', 'nombre_equipo', 'usuario', 'obtener_departamento_usuario', 'nivel', 'equipo', 'tipo_conexion', 'ultima_actualizacion')
    list_max_show_all = 255
    list_per_page = 255
    form = AsignacionAdminForm


@admin.register(models.Configuracion)
class ConfiguracionAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'valor', 'ultima_actualizacion')
    search_fields = ['nombre']


admin.site.site_header = u'Administración del Proxy'
admin.site.site_title = u'Administración del Proxy'
admin.site.index_title = u'Administración'