#!/usr/bin/python -u
# -*- coding: utf-8 -*-
# Filtrado Web para Probar los diferentes Formatos en Squid
# ACL Externa para Squid 3.5
import sys
from urllib import quote


EOF = False
while not EOF:
    line = sys.stdin.readline()
    if not line:
        EOF = True
        continue
    
    sys.stdout.write('OK message={0} log={0}\n'.format(quote(line)))