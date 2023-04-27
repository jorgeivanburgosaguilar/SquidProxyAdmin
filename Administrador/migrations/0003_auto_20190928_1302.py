# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2019-09-28 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Administrador', '0002_auto_20170920_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='asignacion',
            name='nombre_equipo',
            field=models.CharField(help_text='Nombre del equipo o Hostname. Ejemplo: PC1, MAC2, SRV3, SCAN4, etc.', max_length=256, null=True, verbose_name=b'nombre del equipo'),
        ),
        migrations.AddField(
            model_name='historicalasignacion',
            name='nombre_equipo',
            field=models.CharField(help_text='Nombre del equipo o Hostname. Ejemplo: PC1, MAC2, SRV3, SCAN4, etc.', max_length=256, null=True, verbose_name=b'nombre del equipo'),
        ),
    ]
