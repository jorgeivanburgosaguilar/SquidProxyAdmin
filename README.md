# SquidProxyAdmin

Filtro externo para Squid 3.x para implementar un control de acceso por dominio a los usuarios con acceso al proxy.
El filtrado de los usuarios se hace base a la IP del usuario (IPv4).

## Instrucciones para instalar
1. Crear base de datos en postgresql:
   - CREATE DATABASE proxy;
   - CREATE USER proxy WITH PASSWORD 'proxy';
   - GRANT ALL PRIVILEGES ON DATABASE proxy TO proxy;

2. Preparar aplicacion
   - mv example.env .env
   - [Configurar credenciales bd en .env]
   - virtualenv env
   - env\Scripts\activate
   - pip install -r requirements.txt
   - python manage.py makemigrations Administrador
   - python manage.py migrate
   - python manage.py createsuperuser
   - python manage.py collectstatic

4. Configurar servidor web para panel administrativo
   - https://docs.djangoproject.com/en/4.2/howto/deployment/
     - Recomiendo apache con mod_wsgi: https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/modwsgi/

5. Configurar /etc/squid/squid.conf
   - external_acl_type filtrodominio ttl=300 children-max=50 children-startup=4 children-idle=2 ipv4 %SRC %DST /ruta/hacia/python -u /ruta/hacia/SquidProxyAdmin2/cli/filtro_dominio.py
   - acl filtro_dominio external filtrodominio
