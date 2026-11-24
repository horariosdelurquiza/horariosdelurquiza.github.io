"""Arma el sitio de Tren Urquiza horarios.

Uso (desde la raíz del repo):  python fuente/build.py
Escribe index.html, privacidad.html, terminos.html, sw.js, íconos, og.png, manifest y README.md en la raíz.
Variables opcionales: BASE_URL, OUT, CONTACT_EMAIL (activa «Anunciá tu negocio» y «Dejanos tu sugerencia»).
"""
import json, os, statistics, html, shutil
from PIL import Image, ImageDraw, ImageFont

BASE_URL = os.environ.get('BASE_URL', 'https://horariosdelurquiza.github.io/')
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', os.path.dirname(SRC))
DATA = json.load(open(os.path.join(SRC, 'datos', 'horarios.json'), encoding='utf-8'))

ST = [("Federico Lacroze","lacroze"),("José Artigas","artigas"),("Pedro N. Arata","arata"),("Dr. Francisco Beiró","beiro"),
      ("El Libertador","libertador"),("Antonio Devoto","devoto"),("Coronel Francisco Lynch","lynch"),("Fernández Moreno","fmoreno"),
      ("Lourdes","lourdes"),("Tropezón","tropezon"),("José María Bosch","bosch"),("Martín Coronado","coronado"),
      ("Pablo Podestá","podesta"),("Jorge Newbery","newbery"),("Rubén Darío","dario"),("Ejército de los Andes","eandes"),
      ("Juan B. de La Salle","delasalle"),("Sargento Barrufaldi","barrufaldi"),("Capitán Lozano","lozano"),
      ("Teniente Agneta","agneta"),("Campo de Mayo","campodemayo"),("Sargento Cabral","cabral"),("General Lemos","lemos")]
N = len(ST)
DAYS = [('habil','Hábiles'),('sabado','Sábados'),('domingo','Domingos y feriados')]
DAYS_SHORT = {'habil':'Hábiles','sabado':'Sábados','domingo':'Dom. y feriados'}

def expand(day, dirn):
    out = []
    for s in DATA[day][dirn]:
        a, d = s.split('|'); c = int(a); seq = [c]
        for ch in d: c += int(ch); seq.append(c)
        out.append(seq if dirn == 'L' else seq[::-1])  # t[i] = minuto en estación i (0 = Lacroze)
    return out

def hm(m):
    m %= 1440
    return f'{m//60:02d}:{m%60:02d}'

E = html.escape
T = {d: {'L': expand(d,'L'), 'C': expand(d,'C')} for d,_ in DAYS}

# --- primer y último tren
first_last = []
for label, dirn, st in (('Desde Federico Lacroze','L',0), ('Desde General Lemos','C',N-1)):
    cells = []
    for d,_ in DAYS:
        deps = sorted(t[st] for t in T[d][dirn])
        cells.append(f'{hm(deps[0])} – {hm(deps[-1])}')
    first_last.append((label, cells))

# --- cada cuánto pasa (salidas desde Lacroze)
BANDS = [('Madrugada (salen a las)',0,300),('Mañana (5 a 9)',300,540),('Mediodía (9 a 17)',540,1020),('Tarde (17 a 20)',1020,1200),('Noche (20 a 24)',1200,1440)]
def band_txt(deps, a, b):
    if a == 0:
        early = [hm(x) for x in deps if x < b]
        return ', '.join(early) if early else '—'
    gaps = [y-x for x,y in zip(deps, deps[1:]) if a <= x < b]
    if not gaps: return '—'
    if len(gaps) < 3: return f'{round(statistics.median(gaps))} min'
    q = statistics.quantiles(gaps, n=4)
    lo, hi = round(q[0]), round(q[2])
    return f'{lo} min' if lo == hi else f'{lo} a {hi} min'
freq = []
for name, a, b in BANDS:
    row = []
    for d,_ in DAYS:
        deps = sorted(t[0] for t in T[d]['L'])
        row.append(band_txt(deps, a, b))
    freq.append((name, row))

# --- cuánto tarda desde cada cabecera (día hábil, mediana)
def med(vals): return round(statistics.median(vals))
travel = []
for i,(name, slug) in enumerate(ST):
    from_lac = med([t[i]-t[0] for t in T['habil']['L']])
    from_lem = med([t[i]-t[N-1] for t in T['habil']['C']])
    travel.append((i, name, slug, from_lac, from_lem))
full_L = sorted(t[N-1]-t[0] for t in T['habil']['L'])
full_C = sorted(t[0]-t[N-1] for t in T['habil']['C'])
full_min = min(full_L[0], full_C[0]); full_max = max(full_L[-1], full_C[-1])
last_lac = {d: hm(max(t[0] for t in T[d]['L'])) for d,_ in DAYS}
last_lem = {d: hm(max(t[N-1] for t in T[d]['C'])) for d,_ in DAYS}
n_trains = {d: len(T[d]['L']) + len(T[d]['C']) for d,_ in DAYS}

def link_for(i, slug):
    return '#lacroze-lemos' if i == 0 else f'#{slug}-lacroze'

info = []
info.append('  <section class="info" id="info" aria-labelledby="infoTitle">')
info.append('    <div class="block wide">')
info.append('      <h2 id="infoTitle">Horarios del Tren Urquiza</h2>')
info.append(f'      <p class="lead-p">El Tren Urquiza une Federico Lacroze (CABA) con General Lemos (San Miguel) en {full_min} a {full_max} minutos, pasando por 23 estaciones. Arriba elegís de dónde salís y a dónde vas, y te muestra cuándo pasa el próximo tren, a qué hora llegás y por dónde va.</p>')
info.append(f'      <p>Los horarios son los del cuadro oficial «Invierno 2026» publicado por Metrovías, vigente desde el 2 de marzo de 2026: {n_trains["habil"]} trenes por día hábil, {n_trains["sabado"]} los sábados y {n_trains["domingo"]} los domingos y feriados, sumando los dos sentidos.</p>')
info.append('    </div>')

info.append('    <div class="block">')
info.append('      <h2>Primer y último tren</h2>')
info.append('      <div class="tblwrap"><table><thead><tr><th>Día</th><th>Desde Lacroze</th><th>Desde Lemos</th></tr></thead><tbody>')
for k,(d,l) in enumerate(DAYS):
    info.append(f'        <tr><td>{E(l)}</td><td class="tab">{first_last[0][1][k]}</td><td class="tab">{first_last[1][1][k]}</td></tr>')
info.append('      </tbody></table></div>')
info.append('      <h2 style="margin-top:22px">Cada cuánto pasa</h2>')
info.append('      <p class="small">Minutos entre un tren y el siguiente, según las salidas desde Federico Lacroze.</p>')
info.append('      <div class="tblwrap"><table><thead><tr><th>Horario</th>' + ''.join(f'<th>{E(DAYS_SHORT[d])}</th>' for d,_ in DAYS) + '</tr></thead><tbody>')
for name, row in freq:
    info.append(f'        <tr><td>{E(name)}</td>' + ''.join(f'<td>{E(c)}</td>' for c in row) + '</tr>')
info.append('      </tbody></table></div>')
info.append('    </div>')

info.append('    <div class="block">')
info.append('      <h2>Cuánto tarda hasta cada estación</h2>')
info.append('      <p class="small">Minutos de viaje un día hábil. Tocá una estación para ver sus próximos trenes.</p>')
info.append('      <div class="tblwrap"><table><thead><tr><th>Estación</th><th class="num">Desde Lacroze</th><th class="num">Desde Lemos</th></tr></thead><tbody>')
for i, name, slug, fl, fm in travel:
    info.append(f'        <tr><td><a href="{link_for(i, slug)}">{E(name)}</a></td><td class="num">{fl} min</td><td class="num">{fm} min</td></tr>')
info.append('      </tbody></table></div>')
info.append('    </div>')

faq = [
    ('¿Cuánto tarda el tren de Lacroze a Lemos?', f'Entre {full_min} y {full_max} minutos de punta a punta, según el tren.'),
    ('¿Hasta qué hora hay trenes?', f'El último sale de Federico Lacroze a las {last_lac["habil"]} todos los días. De General Lemos sale a las {last_lem["habil"]} los días hábiles, a las {last_lem["sabado"]} los sábados y a las {last_lem["domingo"]} los domingos y feriados.'),
    ('¿Hay trenes los feriados?', 'Sí, con el horario de domingos y feriados. La página detecta sola los feriados nacionales. El tren de las 00:01 que sale de General Lemos no corre los feriados.'),
    ('¿Los horarios son exactos?', 'Metrovías aclara que pueden variar ±3 minutos, así que conviene llegar un rato antes. Si hay demoras o el servicio está cortado, lo avisan en su cuenta de X.'),
    ('¿Dónde está el tren ahora?', 'En «Recorrido» ves por qué estación debería ir cada tren según el horario. No es un GPS: si hay demoras, el tren real puede estar más atrás.'),
]
info.append('    <div class="block wide">')
info.append('      <h2>Preguntas frecuentes</h2>')
for q, a in faq:
    info.append(f'      <h3>{E(q)}</h3><p>{E(a)}</p>')
info.append('      <h3>Estaciones del Tren Urquiza</h3>')
info.append('      <ol class="stlist">' + ''.join(f'<li><a href="{link_for(i, s)}">{E(n)}</a></li>' for i,(n,s) in enumerate(ST)) + '</ol>')
info.append('    </div>')
info.append('  </section>')
INFO = '\n'.join(info)

os.makedirs(OUT, exist_ok=True)
tpl = open(f'{SRC}/template.html', encoding='utf-8').read()
assert '/*DATA*/' in tpl and '<!--INFO-->' in tpl and '{{BASE_URL}}' in tpl
import urllib.parse
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', '')
contacto = ''
if CONTACT_EMAIL:
    contacto = ('<li><a href="anunciar.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10v4h3l6 4V6L6 10H3z"/><path d="M16 9a4 4 0 0 1 0 6M19 6.5a7.5 7.5 0 0 1 0 11"/></svg>Anunciá tu negocio</a></li>\n'
                '      <li><a href="mailto:' + CONTACT_EMAIL + '?subject=Sugerencia%20para%20Tren%20Urquiza%20horarios"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8.5 8.5 0 0 1-12.6 7.4L3 21l1.6-5.2A8.5 8.5 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/></svg>Dejanos tu sugerencia</a></li>')
tpl = tpl.replace('<!--CONTACTO-->', contacto)
page = tpl.replace('/*DATA*/', json.dumps(DATA, separators=(',',':'))).replace('<!--INFO-->', INFO).replace('{{WA_TEXT}}', urllib.parse.quote('Para ver cuándo pasa el próximo tren Urquiza: ' + BASE_URL)).replace('{{BASE_URL}}', BASE_URL)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(page)
import hashlib
ver = hashlib.md5(page.encode('utf-8')).hexdigest()[:10]
open(f'{OUT}/sw.js', 'w', encoding='utf-8').write(open(f'{SRC}/sw_template.js', encoding='utf-8').read().replace('{{VERSION}}', ver))

# --- política de privacidad
priv = open(f'{SRC}/privacidad.html', encoding='utf-8').read()
open(f'{OUT}/privacidad.html', 'w', encoding='utf-8').write(priv)
open(f'{OUT}/terminos.html', 'w', encoding='utf-8').write(open(f'{SRC}/terminos.html', encoding='utf-8').read())

# --- manifest
manifest = {
    "name": "Tren Urquiza horarios", "short_name": "Tren Urquiza", "lang": "es-AR",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#ecede9", "theme_color": "#eaa81c",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}
json.dump(manifest, open(f'{OUT}/manifest.webmanifest', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# --- íconos: frente del tren (mostaza con la franja de ventanas carbón)
MOSTAZA = (234, 168, 28); CARBON = (34, 41, 43); ANDEN = (236, 237, 233); WHITE = (255, 255, 255)
def frente(size, pad, bg):
    S = size * 4
    im = Image.new('RGB', (S, S), bg); d = ImageDraw.Draw(im)
    x0 = y0 = S * pad; x1 = y1 = S * (1 - pad); w = x1 - x0
    d.rounded_rectangle([x0 + w*0.06, y0, x1 - w*0.06, y1], radius=int(w*0.26), fill=MOSTAZA)
    d.rounded_rectangle([x0 + w*0.18, y0 + w*0.13, x1 - w*0.18, y0 + w*0.47], radius=int(w*0.1), fill=CARBON)
    r = w*0.08
    for cx in (x0 + w*0.33, x1 - w*0.33):
        cy = y0 + w*0.72
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=CARBON)
    return im.resize((size, size), Image.LANCZOS)
frente(192, 0.08, ANDEN).save(f'{OUT}/icon-192.png')
frente(512, 0.08, ANDEN).save(f'{OUT}/icon-512.png')
frente(512, 0.2, MOSTAZA).save(f'{OUT}/icon-maskable-512.png')
frente(180, 0.1, ANDEN).save(f'{OUT}/apple-touch-icon.png')
open(f'{OUT}/favicon.svg', 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect x="3" y="1.5" width="26" height="29" rx="8" fill="#eaa81c"/><rect x="6.5" y="5.5" width="19" height="10" rx="3" fill="#22292b"/><circle cx="10.5" cy="23" r="2.4" fill="#22292b"/><circle cx="21.5" cy="23" r="2.4" fill="#22292b"/></svg>')

try:
    # --- imagen para compartir: el costado del coche
    W, H = 1200, 630
    og = Image.new('RGB', (W, H), MOSTAZA); d = ImageDraw.Draw(og)
    bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    cond = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
    reg = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    d.rounded_rectangle([40, 40, W-40, 250], radius=36, fill=CARBON)
    fi = frente(150, 0.0, CARBON); og.paste(fi, (80, 70))
    d.text((270, 88), 'Tren Urquiza', font=ImageFont.truetype(cond, 92), fill=WHITE)
    d.text((272, 190), 'Federico Lacroze – General Lemos', font=ImageFont.truetype(reg, 34), fill=(201, 207, 205))
    d.text((80, 300), 'horarios', font=ImageFont.truetype(cond, 150), fill=CARBON)
    d.text((84, 480), 'Cuándo pasa el próximo tren y cuánto tarda', font=ImageFont.truetype(reg, 40), fill=CARBON)
    d.rectangle([0, H-30, W, H-18], fill=CARBON)
    og.save(f'{OUT}/og.png', optimize=True)
except OSError:
    print('No encontré las tipografías DejaVu: dejo el og.png que ya estaba.')

shutil.copy(f'{SRC}/README-sitio.md', f'{OUT}/README.md')

# --- para buscadores: no indexar la carpeta fuente; mapa del sitio
open(f'{OUT}/.nojekyll', 'w').close()
open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(
    f'User-agent: *\nDisallow: /fuente/\nDisallow: /CLAUDE.md\n\nSitemap: {BASE_URL}sitemap.xml\n')
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{BASE_URL}{p}</loc></url>\n' for p in ('', 'privacidad.html', 'terminos.html'))
    + '</urlset>\n')
print('ok', len(page))
for name,row in freq: print('  ',name,'|',' | '.join(row))
