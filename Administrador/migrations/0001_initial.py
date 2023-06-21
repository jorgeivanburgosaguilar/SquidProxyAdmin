# Generated by Django 4.2 on 2023-06-15 20:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('descripcion', models.TextField()),
                ('ruta', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'categoria',
                'verbose_name_plural': 'categorias',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'departamento',
                'verbose_name_plural': 'departamentos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'equipo',
                'verbose_name_plural': 'equipos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='SitioPermanentementeDenegado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'sitio permanentemente denegado',
                'verbose_name_plural': 'sitios permanentemente denegados',
                'ordering': ['dominio'],
            },
        ),
        migrations.CreateModel(
            name='SitioPermanentementePermitido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'sitio permanentemente permitido',
                'verbose_name_plural': 'sitios permanentemente permitidos',
                'ordering': ['dominio'],
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('activo', models.BooleanField(default=True)),
                ('comentario', models.TextField(blank=True)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.departamento')),
            ],
            options={
                'verbose_name': 'usuario',
                'verbose_name_plural': 'usuarios',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Sitio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.categoria')),
            ],
            options={
                'verbose_name': 'sitio',
                'verbose_name_plural': 'sitios',
                'ordering': ['dominio'],
            },
        ),
        migrations.CreateModel(
            name='Nivel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('filtrar', models.BooleanField(default=True, help_text='Señala si el nivel debe ser procesado por el filtro de sitios web.', verbose_name='filtrar')),
                ('sinaccesoainternet', models.BooleanField(default=False, help_text='Señala si el nivel no tiene permitido acceder a ningun sitio de internet', verbose_name='sin acceso a internet')),
                ('lista_blanca', models.BooleanField(default=False, help_text='Señala si el nivel debe evaluar los filtros como una lista blanca', verbose_name='lista blanca')),
                ('categorias', models.ManyToManyField(blank=True, to='Administrador.categoria', verbose_name='categorias')),
            ],
            options={
                'verbose_name': 'nivel',
                'verbose_name_plural': 'niveles',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalUsuario',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('activo', models.BooleanField(default=True)),
                ('comentario', models.TextField(blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('departamento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='Administrador.departamento')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical usuario',
                'verbose_name_plural': 'historical usuarios',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSitioPermanentementePermitido',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical sitio permanentemente permitido',
                'verbose_name_plural': 'historical sitios permanentemente permitidos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalSitioPermanentementeDenegado',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical sitio permanentemente denegado',
                'verbose_name_plural': 'historical sitios permanentemente denegados',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalNivel',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('filtrar', models.BooleanField(default=True, help_text='Señala si el nivel debe ser procesado por el filtro de sitios web.', verbose_name='filtrar')),
                ('sinaccesoainternet', models.BooleanField(default=False, help_text='Señala si el nivel no tiene permitido acceder a ningun sitio de internet', verbose_name='sin acceso a internet')),
                ('lista_blanca', models.BooleanField(default=False, help_text='Señala si el nivel debe evaluar los filtros como una lista blanca', verbose_name='lista blanca')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical nivel',
                'verbose_name_plural': 'historical niveles',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEquipo',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical equipo',
                'verbose_name_plural': 'historical equipos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalDepartamento',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical departamento',
                'verbose_name_plural': 'historical departamentos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalCategoria',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('descripcion', models.TextField()),
                ('ruta', models.CharField(max_length=256)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical categoria',
                'verbose_name_plural': 'historical categorias',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalAsignacionTemporalUsuario',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('fecha_creacion', models.DateTimeField(blank=True, editable=False, verbose_name='fecha de creacion')),
                ('fecha_expiracion', models.DateField(verbose_name='fecha de expiracion')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='Administrador.usuario')),
            ],
            options={
                'verbose_name': 'historical asignacion temporal del usuario',
                'verbose_name_plural': 'historical asignaciones temporales de los usuarios',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalAsignacionTemporalDepartamento',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('fecha_creacion', models.DateTimeField(blank=True, editable=False, verbose_name='fecha de creacion')),
                ('fecha_expiracion', models.DateField(verbose_name='fecha de expiracion')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('departamento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='Administrador.departamento')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical asignacion temporal del departamento',
                'verbose_name_plural': 'historical asignaciones temporales por departamento',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalAsignacion',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre_equipo', models.CharField(blank=True, help_text='Nombre del equipo o Hostname. Ejemplo: PC1, MAC2, IMP3, SRV4, etc.', max_length=256, verbose_name='nombre del equipo')),
                ('tipo_conexion', models.PositiveSmallIntegerField(choices=[(0, 'Otro'), (1, 'Lan'), (2, 'Wlan')], default=1, validators=[django.core.validators.MaxValueValidator(2)], verbose_name='tipo de conexion')),
                ('ip', models.PositiveSmallIntegerField(db_index=True, validators=[django.core.validators.MaxValueValidator(254)], verbose_name='IP')),
                ('mac', models.CharField(db_index=True, help_text='Dirección MAC en formato largo. Ejemplo: A1:B2:C3:D4:E5:F6', max_length=17, verbose_name='MAC')),
                ('fecha_creacion', models.DateTimeField(blank=True, editable=False, verbose_name='fecha de creacion')),
                ('ultima_actualizacion', models.DateTimeField(blank=True, editable=False, verbose_name='ultima actualizacion')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('equipo', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='Administrador.equipo')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('nivel', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='Administrador.nivel')),
                ('usuario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='Administrador.usuario')),
            ],
            options={
                'verbose_name': 'historical asignacion',
                'verbose_name_plural': 'historical asignaciones',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='AsignacionTemporalUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')),
                ('fecha_expiracion', models.DateField(verbose_name='fecha de expiracion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.usuario')),
            ],
            options={
                'verbose_name': 'asignacion temporal del usuario',
                'verbose_name_plural': 'asignaciones temporales de los usuarios',
                'ordering': ['usuario', 'dominio'],
                'get_latest_by': 'fecha_creacion',
            },
        ),
        migrations.CreateModel(
            name='AsignacionTemporalDepartamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dominio', models.CharField(max_length=256)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')),
                ('fecha_expiracion', models.DateField(verbose_name='fecha de expiracion')),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.departamento')),
            ],
            options={
                'verbose_name': 'asignacion temporal del departamento',
                'verbose_name_plural': 'asignaciones temporales por departamento',
                'ordering': ['departamento', 'dominio'],
                'get_latest_by': 'fecha_creacion',
            },
        ),
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_equipo', models.CharField(blank=True, help_text='Nombre del equipo o Hostname. Ejemplo: PC1, MAC2, IMP3, SRV4, etc.', max_length=256, verbose_name='nombre del equipo')),
                ('tipo_conexion', models.PositiveSmallIntegerField(choices=[(0, 'Otro'), (1, 'Lan'), (2, 'Wlan')], default=1, validators=[django.core.validators.MaxValueValidator(2)], verbose_name='tipo de conexion')),
                ('ip', models.PositiveSmallIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(254)], verbose_name='IP')),
                ('mac', models.CharField(help_text='Dirección MAC en formato largo. Ejemplo: A1:B2:C3:D4:E5:F6', max_length=17, unique=True, verbose_name='MAC')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True, verbose_name='ultima actualizacion')),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.equipo')),
                ('nivel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.nivel')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Administrador.usuario')),
            ],
            options={
                'verbose_name': 'asignacion',
                'verbose_name_plural': 'asignaciones',
                'ordering': ['ip'],
                'get_latest_by': 'fecha_creacion',
            },
        ),
    ]
