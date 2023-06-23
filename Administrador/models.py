'''
Models
'''
from django.db import models
from django.core.validators import MaxValueValidator, validate_ipv46_address
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
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'categoria'
    verbose_name_plural = 'categorias'

  def __str__(self):
    return str(self.nombre)


class Nivel(models.Model):
  nombre = models.CharField(max_length=256)
  filtrar = models.BooleanField(default=True, verbose_name='filtrar',
                                help_text='Señala si el nivel debe ser procesado por el filtro de sitios web.')
  sinaccesoainternet = models.BooleanField(default=False, verbose_name='sin acceso a internet',
                                           help_text='Señala si el nivel no tiene permitido acceder a ningun sitio de internet')
  lista_blanca = models.BooleanField(default=False, verbose_name='lista blanca',
                                     help_text='Señala si el nivel debe evaluar los filtros como una lista blanca')
  categorias = models.ManyToManyField(
    Categoria, blank=True, verbose_name='categorias')
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


class Red(models.Model):
  nombre = models.CharField(max_length=256)
  cidr = models.CharField(max_length=50, verbose_name='CIDR',
                          help_text='Formato CIDR compatible con IPv4 e IPv6')
  inicio_dhcp = models.CharField(max_length=45, blank=True,
                                 validators=[validate_ipv46_address],
                                 verbose_name='Inicio Rango DHCP',
                                 help_text='Formato IPv4 ó IPv6')
  fin_dhcp = models.CharField(max_length=45, blank=True,
                              validators=[validate_ipv46_address],
                              verbose_name='Fin Rango DHCP',
                              help_text='Formato IPv4 ó IPv6')
  history = HistoricalRecords()

  class Meta:
    ordering = ['nombre']
    verbose_name = 'red'
    verbose_name_plural = 'redes'

  def __str__(self):
    return str(self.nombre)


class Asignacion(models.Model):
  class TipoConexion(models.IntegerChoices):
    OTRO = 0
    LAN = 1
    WLAN = 2

  usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
  nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
  nombre_equipo = models.CharField(max_length=256, blank=True, verbose_name='nombre del equipo',
                                   help_text='Nombre del equipo o Hostname. Ejemplo: PC1, MAC2, IMP3, SRV4, etc.')
  equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
  tipo_conexion = models.PositiveSmallIntegerField(choices=TipoConexion.choices, default=TipoConexion.LAN, validators=[
                                                   MaxValueValidator(2)], verbose_name='tipo de conexion')
  red = models.ForeignKey(Red, on_delete=models.CASCADE)
  ip = models.CharField(unique=True, max_length=45,
                        validators=[validate_ipv46_address],
                        verbose_name='IP')
  mac = models.CharField(max_length=17, unique=True, verbose_name='MAC',
                         help_text='Dirección MAC en formato largo. Ejemplo: A1:B2:C3:D4:E5:F6')
  fecha_creacion = models.DateTimeField(
    auto_now_add=True, verbose_name='fecha de creacion')
  ultima_actualizacion = models.DateTimeField(
    auto_now=True, verbose_name='ultima actualizacion')
  history = HistoricalRecords()

  def obtener_departamento_usuario(self):
    'Obtiene el nombre del departamento al que el usuario de la asignacion pertenece'
    return self.usuario.departamento.nombre

  obtener_departamento_usuario.short_description = 'Departamento'

  class Meta:
    ordering = ['ip']
    get_latest_by = 'fecha_creacion'
    verbose_name = 'asignacion'
    verbose_name_plural = 'asignaciones'

  def __str__(self):
    return str(self.ip)
