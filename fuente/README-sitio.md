# Tren Urquiza horarios

Página para ver cuándo pasa el próximo tren de la línea Urquiza (Federico Lacroze ↔ General Lemos), cuánto tarda y por dónde va según el horario.

**Abrir:** https://horariosdelurquiza.github.io/

Para abrir directo en un viaje, agregá al final del link `#origen-destino`, por ejemplo `#coronado-lacroze`.

Nombres de estación para el link: lacroze, artigas, arata, beiro, libertador, devoto, lynch, fmoreno, lourdes, tropezon, bosch, coronado, podesta, newbery, dario, eandes, delasalle, barrufaldi, lozano, agneta, campodemayo, cabral, lemos.

## Cómo se edita

Los archivos de la raíz se generan solos: no se editan a mano. Se cambia lo que está en `fuente/` y se corre `python3 fuente/build.py` desde la raíz. Las notas completas del proyecto están en `CLAUDE.md`.

## Anuncios

- Para ver dónde van los anuncios: abrí la página con `?anuncios` al final (por ejemplo `https://horariosdelurquiza.github.io/?anuncios`).
- Cuando Google AdSense apruebe el sitio, completá `ADS_CLIENT` y `ADS_SLOTS` en `fuente/template.html` (buscá «ANUNCIOS») y volvé a armar el sitio.
- Cuando AdSense dé el ID de editor, agregar el archivo `ads.txt` en la raíz de este repositorio.

## Contador de visitas

- Usa Cloudflare Web Analytics (gratis, sin cookies).
- Crear una cuenta en Cloudflare, ir a Web Analytics, agregar el sitio y copiar el token.
- Pegarlo en `CF_ANALYTICS_TOKEN` dentro de `fuente/template.html` (buscá «CONTADOR DE VISITAS») y volver a armar el sitio.

## Datos

Horarios del cuadro oficial «Invierno 2026» de Metrovías, vigente desde el 2 de marzo de 2026. Página no oficial: pueden variar ±3 minutos.
