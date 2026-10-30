# Curs ASFAN – Introducere în ufologie (seria a patra)

Site-ul cursului gratuit online **„Introducere în ufologie”** (seria a patra, 18 noiembrie 2026 – 26 mai 2027, miercuri 19:00–21:00, prin ZOOM), organizat de **ASFAN** – Asociația pentru studiul fenomenelor aerospațiale neidentificate. Coordonator: Dan D. Farcaș.

**Adresa:** <https://curs.asfan.online> · **ASFAN:** <https://www.asfanufo.ro>

[Română](https://curs.asfan.online/) · [English](https://curs.asfan.online/en/) · [Français](https://curs.asfan.online/fr/) · [Italiano](https://curs.asfan.online/it/) · [Español](https://curs.asfan.online/es/) · [Português](https://curs.asfan.online/pt/) · [Deutsch](https://curs.asfan.online/de/) · [Magyar](https://curs.asfan.online/hu/)

## Conținut

| Ce | Unde |
|---|---|
| Site static, o singură pagină pe limbă (servit de GitHub Pages) | rădăcina depozitului: `index.html` (secțiuni: invitație, program, înscriere, QR) |
| Redirecționări de la adresele vechi (`program.html`, `sesiune-N.html` etc.) și pagina 404 | `*.html` din rădăcină, `404.html` |
| Domeniul propriu | `CNAME` (**nu se șterge**; `build.py` îl regenerează) |
| Celelalte 7 limbi | `en/ fr/ it/ es/ pt/ de/ hu/` (aceeași structură; `hreflang` + `sitemap.xml`) |
| Variantă într-un singur fișier HTML (offline, toate limbile) | se generează în `dist/` (necomisă); variantele livrate sunt pe ramura `variante` |
| Imagini ale afișului, doar pentru varianta cu afiș | `src/art/` |
| Imagini, CSS, JS, fonturi, coduri QR | `assets/` |
| Calendare `.ics` (câte unul pe sesiune + cursul complet, per limbă) | `calendar/` |
| Sursa generatorului și traducerile | `src/` |

Două teme de design (**Moai** și **Anzi**, implicit Moai), reproducând afișele cursului pe desktop, cu variante optimizate pentru tabletă și mobil.

## Regenerare

```bash
pip install segno pillow
python3 src/build.py          # regenerează site-ul (8 limbi) în rădăcina depozitului
python3 src/build_single.py   # regenerează dist/curs-asfan-online.html

# variante (opțional)
SIMPLE=1 python3 src/build.py   # fără titlurile/etichetele derivate: doar textul din plan
# POSTER=1: varianta cu pagina-afiș (copiază întâi src/art/* în assets/)
python3 src/i18n/check.py en  # validează o traducere față de ro.json
```

Textele sunt în `src/i18n/<cod>.json` (sursa: `ro.json`). Pentru o limbă nouă: copiază `ro.json`, tradu valorile (păstrând etichetele HTML și `{substituenții}`), adaugă codul în `LANGS` din `src/build.py` și `src/build_single.py`.

## Credite și licențe

Fonturi: **Montserrat** și **Source Sans 3**, sub licența SIL Open Font License 1.1 (textele în `assets/fonts/OFL-*.txt`), încorporate prin pachetele Fontsource. Imaginile afișului și fotografia aparțin ASFAN / autorilor lor.

## Înscriere

Prin e-mail la adrian.urzica@gmail.com, până la 17 noiembrie 2026 (butonul din site deschide e-mailul precompletat, în română, pentru organizatori; alternative: Gmail și „Copiază mesajul”).

---

## English

Website of ASFAN's free online course *Introduction to Ufology* (4th series, 18 Nov 2026 – 26 May 2027, Wednesdays 19:00–21:00 Romania time, via ZOOM). Static, bilingual-ready build in 8 languages (ro, en, fr, it, es, pt, de, hu), two poster-faithful themes, QR codes, per-session calendar files, and a single-file offline HTML edition. See the table above; regenerate with `src/build.py` and `src/build_single.py`.
