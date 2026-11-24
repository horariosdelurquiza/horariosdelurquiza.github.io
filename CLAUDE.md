# Tren Urquiza horarios

Sitio de una sola página para ver cuándo pasa el próximo tren de la línea Urquiza (Metrovías), entre Federico Lacroze y General Lemos (23 estaciones), y cuánto tarda el viaje. Lo usan pasajeros comunes desde el celular. El dueño lo comparte en grupos de Facebook y quiere ganar algo con anuncios.

**Cómo hablarle al dueño:** en español rioplatense, con "vos". No es programador, así que explicale corto y sin jerga. Cuando termines algo, pasale el link para probarlo en el celular.

## Dónde está

- Sitio: https://horariosdelurquiza.github.io/
- Repositorio: `horariosdelurquiza/horariosdelurquiza.github.io` (organización `horariosdelurquiza`). Se publica con GitHub Pages desde `main`, en la raíz. Hay un `.nojekyll`. Después de un push a `main`, el sitio se actualiza en 1 o 2 minutos.
- Link viejo: https://agustinjjesus.github.io/king-muebles-pruebas/tren-urquiza/ está en el repo `agustinjjesus/king-muebles-pruebas`, carpeta `tren-urquiza/`. Redirige al sitio nuevo, conserva el `#viaje` y desinstala el service worker viejo. No lo toques salvo que te lo pidan.

## Cómo está armado

Los archivos de la raíz (`index.html`, `privacidad.html`, `terminos.html`, `sw.js`, `manifest.webmanifest`, íconos, `og.png`, `robots.txt`, `sitemap.xml`, `README.md`) **se generan**. No los edites a mano. Se edita lo que está en `fuente/` y después se corre, desde la raíz:

```
python3 fuente/build.py
```

Necesita Python 3 con Pillow. Si faltan las tipografías DejaVu, conserva el `og.png` que ya estaba.

- `fuente/template.html`: la página entera (HTML, CSS y JS en un solo archivo). Tiene estas marcas, que el armado reemplaza:
  - `/*DATA*/`: los horarios.
  - `<!--INFO-->`: la sección de información para buscadores (primeros y últimos trenes, frecuencias, minutos por estación, preguntas frecuentes).
  - `{{BASE_URL}}`.
  - `{{WA_TEXT}}`.
  - `<!--CONTACTO-->`.
- `fuente/build.py`: arma todo. Variables opcionales:
  - `BASE_URL`: por defecto la del sitio.
  - `OUT`: por defecto la raíz del repo.
  - `CONTACT_EMAIL`: si está, agrega al pie "Anunciá tu negocio" (link a `anunciar.html`) y "Dejanos tu sugerencia" (mailto).
- `fuente/privacidad.html` y `fuente/terminos.html`: se copian tal cual.
- `fuente/sw_template.js`: el service worker. Su versión es un hash de la página, así que cada vez que cambia la página, los celulares se actualizan solos. Por eso hay que volver a armar después de cualquier cambio. Sirve la página de la red primero y, sin conexión, la del caché.
- `fuente/README-sitio.md`: se copia como `README.md` de la raíz.
- Configuración dentro de `template.html`, cerca del principio del `<script>`:
  - `ADS_CLIENT`, `ADS_SLOTS`: AdSense. Hoy vacíos. Con `?anuncios` en la URL se ven los lugares de los anuncios.
  - `CF_ANALYTICS_TOKEN`: Cloudflare Web Analytics. Vacío por ahora.

Para probar en la compu: `python3 -m http.server` en la raíz y abrir http://localhost:8000. Revisá siempre en un ancho de celular (375 a 390 px) que no haya desplazamiento horizontal.

## Datos de horarios

- Fuente: el PDF oficial de Metrovías "Horarios Urquiza invierno 2026", vigente desde el 2/3/2026.
- Errata del PDF, corregida a mano en `fuente/datos/crudo-invierno-2026.json`: en la tabla a Lacroze de la página 1, el tren 36 dice 10:13 en la fila 16. El horario correcto es 10:23.
- `fuente/datos/horarios.json`, formato compacto:
  - Tipos de día: `habil`, `sabado`, `domingo`. Los feriados usan el horario de domingo.
  - Sentidos: `L` va a General Lemos. `C` va a Federico Lacroze, y su orden de estaciones está invertido.
  - Cada tren se guarda como `"minuto_de_salida|diferencias"`: una cifra por tramo entre estaciones.
  - `flags.noFeriado.domingo.C = [0]`: el tren de las 00:01 desde Lemos no corre los feriados (en el PDF lo marca con «#»).
- Feriados: se calculan en JS (función `feriados`). Incluye:
  - los fijos;
  - Carnaval y Viernes Santo, que dependen de Pascua;
  - los trasladables según la Ley 27.399, con la regla especial de Güemes.

  **No incluye los feriados puente** que el Gobierno fija cada año por decreto. Si hacen falta, hay que agregarlos y confirmar qué horario usa Metrovías esos días.
- La hora siempre es la de Buenos Aires (`Intl`), aunque el celular esté en otra zona. Después de medianoche, la página sigue mostrando los trenes nocturnos del día anterior. Los trenes del día siguiente llevan la marca "mañana".

### Cargar un horario nuevo (por ejemplo, el de verano)

El año pasado, el horario de verano rigió desde el 15/12/2025. Cuando Metrovías publique el PDF nuevo:

1. `python3 fuente/herramientas/leer_pdf.py Horarios.pdf fuente/datos/crudo-NUEVO.json`. Necesita `pdftotext` (poppler). Espera 6 páginas con 2 tablas de 23 filas cada una: páginas 1 a 3 hábiles, 4 y 5 sábados, 6 domingos. Si la estructura cambió, adaptalo.
2. `python3 fuente/herramientas/revisar.py fuente/datos/crudo-NUEVO.json`. Marca saltos raros, o sea erratas. Corregilas a mano en el crudo.
3. `python3 fuente/herramientas/armar_datos.py fuente/datos/crudo-NUEVO.json fuente/datos/horarios.json`. Revisá que el tren con «#» siga siendo el mismo.
4. Actualizá el texto que nombra el cuadro vigente («Invierno 2026», vigente desde el 2 de marzo de 2026) en `template.html`, `build.py`, `terminos.html` y `README-sitio.md`.
5. `python3 fuente/build.py`. Después compará 3 o 4 horarios contra el PDF a mano.

Si hay dos cuadros con fechas, una opción es guardar los dos y que la página elija según la fecha.

## Diseño (no lo cambies sin que te lo pidan)

El dueño pidió que la página **no parezca hecha con IA** y que use el color del tren. Ya rechazó el modo oscuro y una tipografía tipo pixel.

- Colores:

  | Nombre | Uso | Color |
  |---|---|---|
  | andén | fondo | `#ecede9` |
  | papel | tarjetas | `#fff` |
  | carbón | texto y franja de ventanas | `#22292b` |
  | riel | texto secundario | `#697271` |
  | junta | bordes | `#d5d8d3` |
  | mostaza Metrovías | el tren | `#eaa81c` |
  | mostaza para texto | | `#865b00` |
  | turquesa | color de la línea | `#00a79f` |
  | turquesa para texto | | `#006f69` |
  | tinta | | `#d9f1ef` |

- Tipografía: Archivo variable (ancho de 62 a 125), de Omnibus-Type, de Buenos Aires.
- Siempre tema claro (`color-scheme: light only`).
- El tablero principal es el costado de un coche mostaza con una franja carbón de ventanas que dice "Tren a <terminal>". El logo es el frente del tren.
- Textos:
  - Nada de etiquetas en MAYÚSCULAS ni frases unidas con "·".
  - Sin emojis.
  - Mayúscula solo al principio.
  - Frases cortas y claras.

## Qué hace la página

- Elegir el origen y el destino. Recuerda el último viaje y los recientes. También abre directo con un link como `#coronado-lacroze`; los nombres de estación para el link están en `README-sitio.md`.
- Botón para invertir el viaje.
- Próximo tren con cuenta regresiva, hora de llegada y duración del viaje.
- "Pasó hace X min, quizás todavía está" para el tren que acaba de salir.
- Lista de los trenes que siguen y opción de ver todos los del día.
- Elegir otro día u otra hora.
- Modo "llego a las": qué tren tomar para llegar a cierta hora.
- Diagrama del recorrido con la posición estimada del tren.
- Estación más cercana con la ubicación del celular.
- Aviso antes del tren (2, 5, 10 o 15 min): suena, vibra y manda una notificación.
- Datos de combinaciones por estación y link al mapa.
- Avisos de Metrovías: muestra los últimos posts de @Metrovias en X.
- Compartir: botón del sistema y botón de WhatsApp.
- Instalar como app (ícono en el celular), con instrucciones para iPhone. Además del botón del pie, hay un aviso chico debajo del tablero, solo en celulares, que se puede cerrar con "Ahora no".
- Abajo, la información para buscadores (tablas y preguntas frecuentes) está en bloques que se abren y se cierran con un toque. En pantallas grandes empiezan abiertos.
- Funciona sin conexión.

Claves que guarda en `localStorage`: `urq.recent`, `urq.last`, `urq.avisos`, `urq.alarm`, `urq.lead`, `urq.icono` (el aviso del ícono ya se cerró).

## Pendientes

1. **Publicar el pie nuevo** (Términos y condiciones, Política de privacidad, Anunciá tu negocio, Dejanos tu sugerencia, Crear ícono en el celular) y la página `terminos.html`. Ya está todo en `fuente/`, falta armar y subir: corré `python3 fuente/build.py`, revisá y hacé commit.
2. **Mail de contacto:** cuando el dueño lo pase, armá el sitio con `CONTACT_EMAIL=...` y creá `fuente/anunciar.html`. Tiene que ser una página simple, con el mismo estilo que `terminos.html`, para comercios que quieran anunciar. El armado tiene que copiarla igual que a `terminos.html`, y hay que sumarla a `CORE` y `pageKey` en `sw_template.js` y al `sitemap.xml`. Preguntale si también quiere poner un WhatsApp.
3. **Contador de visitas:** cuando pase el token de Cloudflare Web Analytics, completá `CF_ANALYTICS_TOKEN`.
4. **AdSense:** cuando lo aprueben:
   - completá `ADS_CLIENT` y `ADS_SLOTS`;
   - creá `ads.txt` en la raíz con `google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0`, cambiando las X por su número de editor;
   - agregá `ads.txt` al armado para que no se pierda.
5. **Horario de verano:** cargarlo cuando salga el PDF (ver arriba).
6. **Ideas para más adelante:**
   - una página por estación para aparecer en Google ("horarios tren Urquiza Martín Coronado");
   - los feriados puente.

## Commits

Mensajes cortos y en español. Antes de cada commit, armá el sitio para que los archivos de la raíz coincidan con `fuente/`.
