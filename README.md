# SquidProxyAdmin

Filtro externo para Squid 3.x para implementar un control de acceso por dominio, mime y la extension de los archivos a los usuarios con acceso al proxy.
El filtrado de los usuarios se hace base a la IP del usuario.

## Instrucciones para hacer funcionar el proyecto en windows

1. Descargamos la dependencia psycopg2 en su version 2.5.4 de http://www.stickpeople.com/projects/python/win-psycopg/
    - Para python 2.7 en un equipo a 64-bits seria: psycopg2-2.5.4.win-amd64-py2.7-pg9.3.5-release.exe

2. Instalar dependencia
    - El instalador pone la dependencia a nivel global, si no se requiere instalar a nivel global
      seguir las instrucciones del paso 4 para instalar exclusivamente en el entorno virtual.

2. Regenerar (borrar el entorno en "Python Environments" anterior y crear uno nuevo) el entorno virtual con el archivo requirements.txt
   (Python Tools for Visual Studio 2.1 debe reconocer este archivo e instalar las dependencias necesarias)
    - Debe generar un error de que no pudo instalar la dependencia psycopg2 por un error de compilacion

4. Para instalar esta dependencia exclusivamente en el entorno virtual del proyecto:
    - Abrimos una consola, nos movemos hasta donde esta el proyecto y ejecutamos:
        - env\Scripts\activate
        - env\Scripts\easy_install.exe X:\ruta\donde\se\descargo\la\libreria.exe
        - env\Scripts\deactivate
        - exit
    - Seleccionamos el entorno recientemente creado (el que fallo previamente) en "Python Environments" con el clic derecho y ponemos
      "Install from requirements.txt" para verificar que las dependencias esten correctamente instaladas

## Instrucciones para despleguar en Linux por primera vez

1. Ejecutar desde la carpeta de la aplicacion
    - pip install -r requirements.txt
    - python manage.py collectstatic
    - python manage.py migrate
    - python manage.py makemigrations Administrador
    - python manage.py migrate
    - python manage.py createsuperuser
    - python ActualizarSitios.py

2. Configurar apache

3. Probar que funcione
