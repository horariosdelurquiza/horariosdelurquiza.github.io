"""Lee un PDF oficial de horarios del Urquiza (con texto, como el de invierno 2026) y guarda los horarios crudos.

Uso: python fuente/herramientas/leer_pdf.py Horarios.pdf fuente/datos/crudo-NUEVO.json
Necesita pdftotext (poppler). Espera 6 páginas con 2 tablas de 23 filas cada una:
páginas 1-3 días hábiles, 4-5 sábados, 6 domingos y feriados; tabla 0 = a General Lemos, tabla 1 = a Federico Lacroze.
Si el PDF nuevo tiene otra estructura, revisá antes de seguir.
"""
import re, subprocess, json, sys
pdf, out = sys.argv[1], sys.argv[2]
T = re.compile(r'\d{1,2}:\d{2}')
res = {}
for p in range(1, 7):
    txt = subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), pdf, '-'], capture_output=True, text=True).stdout
    blocks, cur = [], []
    for line in txt.split('\n'):
        toks = T.findall(line)
        if toks: cur.append([x.zfill(5) for x in toks])
        elif cur: blocks.append(cur); cur = []
    if cur: blocks.append(cur)
    print('página', p, 'tablas', [len(b) for b in blocks], 'columnas', [sorted(set(len(r) for r in b)) for b in blocks])
    for t, b in enumerate(blocks):
        res[f'{p}-{t}'] = b
json.dump(res, open(out, 'w'))
print('guardado en', out)
