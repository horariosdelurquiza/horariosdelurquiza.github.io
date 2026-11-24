"""Revisa que cada tren tenga horarios crecientes y tiempos razonables entre estaciones.

Uso: python fuente/herramientas/revisar.py fuente/datos/crudo-NUEVO.json
Marca saltos raros (por ejemplo erratas del PDF). Corregilas a mano en el JSON crudo antes de armar los datos.
"""
import json, sys
import statistics
raw = json.load(open(sys.argv[1]))
def m(s): h, mi = s.split(':'); return int(h)*60 + int(mi)
probs = 0
for key, rows in raw.items():
    R, C = len(rows), len(rows[0])
    if R != 23 or any(len(r) != C for r in rows): print(key, 'filas/columnas raras', R, set(len(r) for r in rows)); probs += 1; continue
    M = [[m(x) for x in r] for r in rows]
    for i in range(R-1):
        diffs = [(M[i+1][j]-M[i][j]) % 1440 for j in range(C)]
        med = statistics.median(diffs)
        for j, dd in enumerate(diffs):
            if dd > 6 or abs(dd-med) > 3:
                print(key, 'fila', i, '->', i+1, 'columna', j, rows[i][j], rows[i+1][j], 'salto', dd, 'normal', med); probs += 1
    print(key, 'trenes', C, 'primero', rows[0][0], 'último', rows[0][-1])
print('problemas:', probs)
