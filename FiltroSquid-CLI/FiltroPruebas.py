#!/usr/bin/env python
'''
Filtrado Web para Probar los diferentes Formatos en Squid
ACL Externa para Squid 3.5
'''
import sys
from urllib.parse import quote

EOF = False
while not EOF:
  line = sys.stdin.readline()
  if not line:
    EOF = True
    continue

  sys.stdout.write(f'OK message={line} log={quote(line)}\n')
