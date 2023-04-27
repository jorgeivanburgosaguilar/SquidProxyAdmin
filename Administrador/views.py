# -*- coding: utf-8 -*-
from django.shortcuts import render
from Administrador.models import Asignacion


def index(request):
    asignaciones = Asignacion.objects.all().values('ip', 'mac', 'usuario__nombre', 'usuario__departamento__nombre', 'nivel__nombre', 'equipo__nombre', 'tipo_conexion', 'nombre_equipo')
    return render(request, 'Administrador/index.html', {'asignaciones': asignaciones})