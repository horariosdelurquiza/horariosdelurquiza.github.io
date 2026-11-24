"""Convierte los horarios crudos al formato compacto que usa la página (fuente/datos/horarios.json).

Uso: python fuente/herramientas/armar_datos.py fuente/datos/crudo-NUEVO.json fuente/datos/horarios.json
Formato: por tipo de día (habil, sabado, domingo) y sentido (L = a Lemos, C = a Lacroze), cada tren es
"minuto_de_salida|diferencias" con una cifra por tramo entre estaciones, en el orden de la tabla.
flags.noFeriado marca trenes de domingo que no corren los feriados (el 00:01 desde Lemos, con «#» en el PDF).
"""
import json, sys
raw = json.load(open(sys.argv[1]))
def m(s): h, mi = s.split(':'); return int(h)*60 + int(mi)
days = {'habil': [1, 2, 3], 'sabado': [4, 5], 'domingo': [6]}
out = {}
for d, pages in days.items():
    out[d] = {}
    for t, dirn in ((0, 'L'), (1, 'C')):
        trains = []
        for p in pages:
            rows = raw[f'{p}-{t}']
            for j in range(len(rows[0])):
                col = [m(rows[i][j]) for i in range(23)]
                deltas = [(col[i+1]-col[i]) % 1440 for i in range(22)]
                assert max(deltas) <= 9, ('tramo de más de 9 min', d, dirn, j)
                trains.append(f"{col[0]}|{''.join(map(str, deltas))}")
        out[d][dirn] = trains
out['flags'] = {'noFeriado': {'domingo': {'C': [0]}}}
print('Revisá que el primer tren de domingo a Lacroze siga siendo el de las 00:01 con «#»:', out['domingo']['C'][0])
json.dump(out, open(sys.argv[2], 'w'), separators=(',', ':'))
print({d: {k: len(v) for k, v in out[d].items()} for d in days})
