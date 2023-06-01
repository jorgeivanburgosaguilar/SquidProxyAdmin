# SquidProxyAdmin

Filtro externo para Squid 3.x para implementar un control de acceso por dominio, mime y la extension de los archivos a los usuarios con acceso al proxy.
El filtrado de los usuarios se hace base a la IP del usuario para una red IPv4 clase C (/24).

## Instrucciones para instalar
1. Crear base de datos en postgresql:
   - CREATE DATABASE proxy;
   - CREATE USER proxy WITH PASSWORD 'proxy';
   - GRANT ALL PRIVILEGES ON DATABASE proxy TO proxy;

2. Preparar aplicacion
   - virtualenv env
   - env\Scripts\activate
   - pip install -r requirements.txt
   - python manage.py makemigrations Administrador
   - python manage.py migrate
   - python manage.py createsuperuser
   - python manage.py collectstatic

3. Configurar servidor web para panel administrativo
   - https://docs.djangoproject.com/en/4.2/howto/deployment/
     - Recomiendo apache con mod_wsgi: https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/modwsgi/

4. Configurar /etc/squid/squid.conf
   - external_acl_type filtrodominio ttl=300 children-max=50 children-startup=4 children-idle=2 ipv4 %SRC %DST /ruta/hacia/python -u /ruta/hacia/SquidProxyAdmin2/FiltroSquid-CLI/FiltroDominio.py
   - acl filtro_dominio external filtrodominio
   - external_acl_type filtroextensionarchivo ttl=300 children-max=50 children-startup=4 ipv4 children-idle=2 %SRC %PATH /ruta/hacia/python -u /ruta/hacia/SquidProxyAdmin2/FiltroSquid-CLI/FiltroExtensionArchivo.py
   - acl filtro_extension_archivo external filtroextensionarchivo
   - external_acl_type filtromime ttl=300 children-max=50 children-startup=2 children-idle=2 ipv4 %SRC %<h{Content-Type} /ruta/hacia/python -u /ruta/hacia/SquidProxyAdmin2/FiltroSquid-CLI/FiltroMIME.py
   - acl filtro_mime external filtromime
