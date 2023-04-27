# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-09-20 14:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Administrador', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalCategoria',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256)),
                ('descripcion', models.TextField()),
                ('ruta', models.CharField(max_length=256)),
                ('interna', models.BooleanField(default=False, help_text='Se\xf1ala si la categoria es de uso interno por lo que los scripts de automatizacion no la deben borrar', verbose_name=b'interna')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical categoria',
            },
        ),
        migrations.CreateModel(
            name='HistoricalExtensionArchivo',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('extension', models.CharField(max_length=20)),
                ('actualizaciones', models.BooleanField(default=False, help_text='Se\xf1ala si la extension del archivo se debe permitir durante el modo de actualizaci\xf3n', verbose_name=b'actualizaciones')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical extension de archivo',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTipoMime',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('mime', models.CharField(max_length=256, verbose_name=b'MIME')),
                ('actualizaciones', models.BooleanField(default=False, help_text='Se\xf1ala si el tipo de MIME se debe permitir durante el modo actualizaci\xf3n', verbose_name=b'actualizaciones')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical tipo de MIME',
            },
        ),
        migrations.AddField(
            model_name='categoria',
            name='interna',
            field=models.BooleanField(default=False, help_text='Se\xf1ala si la categoria es de uso interno por lo que los scripts de automatizacion no la deben borrar', verbose_name=b'interna'),
        ),
        migrations.AddField(
            model_name='historicalnivel',
            name='lista_blanca',
            field=models.BooleanField(default=False, help_text='Se\xf1ala si el nivel debe evaluar los filtros como una lista blanca', verbose_name=b'lista blanca'),
        ),
        migrations.AddField(
            model_name='nivel',
            name='lista_blanca',
            field=models.BooleanField(default=False, help_text='Se\xf1ala si el nivel debe evaluar los filtros como una lista blanca', verbose_name=b'lista blanca'),
        ),
    ]