'''
Models
'''
from django.db import models
from django.core.validators import MaxValueValidator
from simple_history.models import HistoricalRecords


class Departamento(models.Model):
  nombre = models.CharField(max_length=256)
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'departamento'
    verbose_name_plural = 'departamentos'

  def __str__(self):
    return str(self.nombre)


class Usuario(models.Model):
  nombre = models.CharField(max_length=256)
  departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
  activo = models.BooleanField(default=True)
  comentario = models.TextField(blank=True)
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'usuario'
    verbose_name_plural = 'usuarios'

  def __str__(self):
    return str(self.nombre)


class Categoria(models.Model):
  nombre = models.CharField(max_length=256)
  descripcion = models.TextField()
  ruta = models.CharField(max_length=256)
  interna = models.BooleanField(default=False, verbose_name='interna',
                                help_text='Señala si la categoria es de uso interno por lo que los scripts de automatizacion no la deben borrar')
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'categoria'
    verbose_name_plural = 'categorias'

  def __str__(self):
    return str(self.nombre)


class TipoMime(models.Model):
  mime = models.CharField(max_length=256, verbose_name='MIME')
  actualizaciones = models.BooleanField(default=False, verbose_name='actualizaciones',
                                        help_text='Señala si el tipo de MIME se debe permitir durante el modo actualización')
  history = HistoricalRecords()

  class Meta:
    ordering = ['mime']
    verbose_name = 'tipo de MIME'
    verbose_name_plural = 'tipos de MIME'

  def __str__(self):
    return str(self.mime)


class ExtensionArchivo(models.Model):
  extension = models.CharField(max_length=256)
  actualizaciones = models.BooleanField(default=False, verbose_name='actualizaciones',
                                        help_text='Señala si la extension del archivo se debe permitir durante el modo de actualización')
  history = HistoricalRecords()

  class Meta:
    ordering = ['extension']
    verbose_name = 'extension de archivo'
    verbose_name_plural = 'extensiones de archivos'

  def __str__(self):
    return str(self.extension)


class Nivel(models.Model):
  nombre = models.CharField(max_length=256)
  filtrar = models.BooleanField(default=True, verbose_name='filtrar',
                                help_text='Señala si el nivel debe ser procesado por el filtro de sitios web.')
  sinaccesoainternet = models.BooleanField(default=False, verbose_name='sin acceso a internet',
                                           help_text='Señala si el nivel no tiene permitido acceder a ningun sitio de internet')
  actualizaciones = models.BooleanField(default=True, verbose_name='actualizaciones',
                                        help_text='Señala si el nivel puede entrar en modo de actualización')
  lista_blanca = models.BooleanField(default=False, verbose_name='lista blanca',
                                     help_text='Señala si el nivel debe evaluar los filtros como una lista blanca')
  categorias = models.ManyToManyField(
    Categoria, blank=True, verbose_name='categorias')
  tipos_mime = models.ManyToManyField(
    TipoMime, blank=True, verbose_name='tipos de MIME')
  extensiones_archivos = models.ManyToManyField(
    ExtensionArchivo, blank=True, verbose_name='extensiones de archivos')
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'nivel'
    verbose_name_plural = 'niveles'

  def __str__(self):
    return str(self.nombre)


class Sitio(models.Model):
  categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
  dominio = models.CharField(max_length=256)

  class Meta:
    ordering = ['dominio']
    verbose_name = 'sitio'
    verbose_name_plural = 'sitios'

  def __str__(self):
    return str(self.dominio)


class SitioPermanentementePermitido(models.Model):
  dominio = models.CharField(max_length=256)
  history = HistoricalRecords()

  class Meta:
    ordering = ['dominio']
    verbose_name = 'sitio permanentemente permitido'
    verbose_name_plural = 'sitios permanentemente permitidos'

  def __str__(self):
    return str(self.dominio)


class SitioPermanentementeDenegado(models.Model):
  dominio = models.CharField(max_length=256)
  history = HistoricalRecords()

  class Meta:
    ordering = ['dominio']
    verbose_name = 'sitio permanentemente denegado'
    verbose_name_plural = 'sitios permanentemente denegados'

  def __str__(self):
    return str(self.dominio)


class AsignacionTemporalDepartamento(models.Model):
  departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
  dominio = models.CharField(max_length=256)
  fecha_creacion = models.DateTimeField(
    auto_now_add=True, verbose_name='fecha de creacion')
  fecha_expiracion = models.DateField(verbose_name='fecha de expiracion')
  history = HistoricalRecords()

  class Meta:
    ordering = ['departamento', 'dominio']
    get_latest_by = 'fecha_creacion'
    verbose_name = 'asignacion temporal del departamento'
    verbose_name_plural = 'asignaciones temporales por departamento'

  def __str__(self):
    return str(self.dominio)


class AsignacionTemporalUsuario(models.Model):
  usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
  dominio = models.CharField(max_length=256)
  fecha_creacion = models.DateTimeField(
    auto_now_add=True, verbose_name='fecha de creacion')
  fecha_expiracion = models.DateField(verbose_name='fecha de expiracion')
  history = HistoricalRecords()

  class Meta:
    ordering = ['usuario', 'dominio']
    get_latest_by = 'fecha_creacion'
    verbose_name = 'asignacion temporal del usuario'
    verbose_name_plural = 'asignaciones temporales de los usuarios'

  def __str__(self):
    return str(self.dominio)


class Equipo(models.Model):
  nombre = models.CharField(max_length=256)
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'equipo'
    verbose_name_plural = 'equipos'

  def __str__(self):
    return str(self.nombre)


class Asignacion(models.Model):
  class TipoConexion(models.IntegerChoices):
    OTRO = 0
    LAN = 1
    WLAN = 2

  IP_CHOICES = [(i, f'192.168.2.{i}' % i) for i in range(1, 255)]
  usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
  nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
  nombre_equipo = models.CharField(max_length=256, blank=True, verbose_name='nombre del equipo',
                                   help_text='Nombre del equipo o Hostname. Ejemplo: PC1, MAC2, IMP3, SRV4, etc.')
  equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
  tipo_conexion = models.PositiveSmallIntegerField(choices=TipoConexion.choices, default=TipoConexion.LAN, validators=[
                                                   MaxValueValidator(2)], verbose_name='tipo de conexion')
  ip = models.PositiveSmallIntegerField(choices=IP_CHOICES, unique=True, validators=[
                                        MaxValueValidator(254)], verbose_name='IP')
  mac = models.CharField(max_length=17, unique=True, verbose_name='MAC')
  fecha_creacion = models.DateTimeField(
    auto_now_add=True, verbose_name='fecha de creacion')
  ultima_actualizacion = models.DateTimeField(
    auto_now=True, verbose_name='ultima actualizacion')
  history = HistoricalRecords()

  def obtener_ips_disponibles(self, para_admin=False):
    'Obtiene las IPs que quedan disponibles incluyendo la de la instancia actual.'
    ips_rango_dinamico = range(195, 200)
    ips_asignadas = Asignacion.objects.values_list('ip', flat=True)
    ips_ocupadas = list(ips_asignadas) + ips_rango_dinamico
    ips_disponibles = []

    if para_admin:
      ips_disponibles.append(('', '---------'))

    for choice in self.IP_CHOICES:
      if (choice[0] not in ips_ocupadas) or (choice[0] == self.ip):
        ips_disponibles.append(choice)

    return ips_disponibles

  def obtener_departamento_usuario(self):
    'Obtiene el nombre del departamento al que el usuario de la asignacion pertenece'
    return self.usuario.departamento.nombre

  obtener_departamento_usuario.short_description = 'Departamento'

  def obtener_ip(self):
    'Obtiene la IP completa relacionada con la asignacion'
    return self.IP_CHOICES[self.ip - 1][1]

  obtener_ip.short_description = 'IP'
  obtener_ip.admin_order_field = 'ip'

  class Meta:
    ordering = ['ip']
    get_latest_by = 'fecha_creacion'
    verbose_name = 'asignacion'
    verbose_name_plural = 'asignaciones'

  def __str__(self):
    return self.obtener_ip()


class Configuracion(models.Model):
  nombre = models.CharField(max_length=256)
  valor = models.CharField(max_length=256)
  ultima_actualizacion = models.DateTimeField(
    auto_now=True, verbose_name='ultima actualizacion')
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'configuracion'
    verbose_name_plural = 'configuraciones'

  def __str__(self):
    return str(self.nombre)
