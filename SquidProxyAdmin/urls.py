"""
URL configuration for SquidProxyAdmin project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('Administrador.urls')),
    path('admin/', admin.site.urls),
]
