# Curs ASFAN – Introducere în ufologie (seria a patra)

Site-ul cursului gratuit online **„Introducere în ufologie”** (seria a patra, 18 noiembrie 2026 – 26 mai 2027, miercuri 19:00–21:00, prin ZOOM), organizat de **ASFAN** – Asociația pentru studiul fenomenelor aerospațiale neidentificate. Coordonator: Dan D. Farcaș.

**Adresa:** <https://curs.asfan.online> · **ASFAN:** <https://www.asfanufo.ro>

[Română](https://curs.asfan.online/) · [English](https://curs.asfan.online/en/) · [Français](https://curs.asfan.online/fr/) · [Italiano](https://curs.asfan.online/it/) · [Español](https://curs.asfan.online/es/) · [Português](https://curs.asfan.online/pt/) · [Deutsch](https://curs.asfan.online/de/) · [Magyar](https://curs.asfan.online/hu/)

## Conținut

| Ce | Unde |
|---|---|
| Site static (servit direct, ex. GitHub Pages) | rădăcina depozitului: `index.html`, `program.html`, `detalii.html`, `inscriere.html`, `qr.html`, `sesiune-1…14.html` |
| Celelalte 7 limbi | `en/ fr/ it/ es/ pt/ de/ hu/` (aceeași structură; `hreflang` + `sitemap.xml`) |
| Variantă într-un singur fișier HTML (imagini, fonturi și toate limbile încorporate, funcționează offline) | `curs-asfan-online.html` |
| Imagini, CSS, JS, fonturi, coduri QR | `assets/` |
| Calendare `.ics` (câte unul pe sesiune + cursul complet, per limbă) | `calendar/` |
| Sursa generatorului și traducerile | `src/` |

Două teme de design (**Moai** și **Anzi**, implicit Anzi), reproducând afișele cursului pe desktop, cu variante optimizate pentru tabletă și mobil.

## Regenerare

```bash
pip install segno pillow
python3 src/build.py          # regenerează site-ul (8 limbi) în rădăcina depozitului
python3 src/build_single.py   # regenerează curs-asfan-online.html
python3 src/i18n/check.py en  # validează o traducere față de ro.json
```

Textele sunt în `src/i18n/<cod>.json` (sursa: `ro.json`). Pentru o limbă nouă: copiază `ro.json`, tradu valorile (păstrând etichetele HTML și `{substituenții}`), adaugă codul în `LANGS` din `src/build.py` și `src/build_single.py`.

## Înscriere

Prin e-mail la adrian.urzica@gmail.com, până la 17 noiembrie 2026 (formularul din site pregătește e-mailul, scris în română, pentru organizatori).

---

## English

Website of ASFAN's free online course *Introduction to Ufology* (4th series, 18 Nov 2026 – 26 May 2027, Wednesdays 19:00–21:00 Romania time, via ZOOM). Static, bilingual-ready build in 8 languages (ro, en, fr, it, es, pt, de, hu), two poster-faithful themes, QR codes, per-session calendar files, and a single-file offline HTML edition. See the table above; regenerate with `src/build.py` and `src/build_single.py`.
