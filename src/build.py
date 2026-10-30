#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generează site-ul static multilingv curs.asfan.online în ./site (ro la rădăcină, celelalte limbi în ./site/<cod>/)"""
import os, json, html, datetime as dt, shutil
import segno

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT") or os.path.join(ROOT, "site")
POSTER = os.environ.get("POSTER") == "1"
SIMPLE = os.environ.get("SIMPLE") == "1"   # fără titluri/etichete derivate: doar textul din plan
SITE = "https://curs.asfan.online"
ASFAN = "https://www.asfanufo.ro"
MAIL = "adrian.urzica@gmail.com"
LANGS = ["ro", "en", "fr", "it", "es", "pt", "de", "hu"]
DATA = {l: json.load(open(f"{ROOT}/i18n/{l}.json", encoding="utf-8")) for l in LANGS}
os.makedirs(OUT + "/calendar", exist_ok=True)
os.makedirs(OUT + "/assets", exist_ok=True)

# (data, teme afiș) — independente de limbă
SDATES = [((2026,11,18),[1]),((2026,12,2),[2,11]),((2026,12,16),[9]),((2027,1,13),[4]),((2027,2,24),[5]),((2027,3,3),[6]),
          ((2027,3,10),[10]),((2027,3,24),[6]),((2027,3,31),[12]),((2027,4,7),[7]),((2027,4,21),[13]),((2027,4,28),[12]),
          ((2027,5,12),[3,8]),((2027,5,26),[14])]
TOPIC_SESS = {1:1,2:2,3:13,4:4,5:5,6:6,7:10,8:13,9:3,10:7,11:2,12:12,13:11,14:14}
assert all(dt.date(*d).weekday() == 2 for d, _ in SDATES), 'toate sesiunile trebuie să fie miercuri'
assert [d for d, _ in SDATES] == sorted(d for d, _ in SDATES)

E = html.escape
import hashlib
BUILD_UTC = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BUILD_SEQ = int((dt.datetime.now(dt.timezone.utc) - dt.datetime(2026,10,30,tzinfo=dt.timezone.utc)).total_seconds() // 3600)
def av(rel): return hashlib.md5(open(f"{OUT}/assets/{rel}","rb").read()).hexdigest()[:8]
CODE = "ro"; LD = DATA["ro"]; UI = LD["ui"]; P = ""; CAL = "calendar/"; SESS = []

def rep(s, **kw):
    s = s.replace("{MAIL}", MAIL).replace("{SITE}", SITE).replace("{ASFAN}", ASFAN)
    for k, v in kw.items(): s = s.replace("{" + k + "}", str(v))
    return s
def T(key, **kw): return rep(UI[key], **kw)
def A(key, **kw): return E(T(key, **kw), quote=True)          # pentru atribute
def JS(key): return E(LD["js"][key], quote=True)
def fmtd(date, kind):
    D = LD["dates"]
    return (D["fmt_" + kind].replace("{wd}", D["wd"][date.weekday()]).replace("{d}", str(date.day))
            .replace("{month}", D["months"][date.month]).replace("{mon3}", D["mon3"][date.month]).replace("{y}", str(date.year)))
def build_sess():
    out = []
    for i, ((d, topics), tx) in enumerate(zip(SDATES, LD["sessions"]), 1):
        date = dt.date(*d); off = 3 if date >= dt.date(2027, 3, 28) else 2   # EET / EEST
        st = dt.datetime(*d, 19, 0); en = dt.datetime(*d, 21, 0)
        out.append(dict(n=i, date=date, off=off, title=tx["title"], text=tx["text"], chips=tx["chips"], topics=topics,
            label=fmtd(date, "long"), short=fmtd(date, "short"),
            start=f"{st.isoformat()}+0{off}:00", end=f"{en.isoformat()}+0{off}:00",
            utc_s=(st - dt.timedelta(hours=off)).strftime("%Y%m%dT%H%M%SZ"), utc_e=(en - dt.timedelta(hours=off)).strftime("%Y%m%dT%H%M%SZ")))
    return out

# ------------------------------------------------------------------ QR
def make_qr(url, name):
    q = segno.make(url, error="m", boost_error=True)
    q.save(f"{OUT}/assets/{name}.svg", scale=10, border=4, dark="#000000", light="#ffffff", xmldecl=False, svgns=True)
    q.save(f"{OUT}/assets/{name}.png", scale=24, border=4, dark="#000000", light="#ffffff")
make_qr(SITE + "/", "qr-curs"); make_qr(ASFAN, "qr-asfan")

# ------------------------------------------------------------------ ICS (per limbă)
def esc(s): return s.replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
def page_url(n): return SITE + "/" + (CODE + "/" if CODE != "ro" else "") + f"#s{n}"
def vevent(s):
    desc = f"{s['title']}\n\n{s['text']}\n\n" + T("ics_desc", url=page_url(s['n']))
    return ["BEGIN:VEVENT", f"UID:asfan-ufologie-4-s{s['n']}-{CODE}@curs.asfan.online", f"DTSTAMP:{BUILD_UTC}", f"SEQUENCE:{BUILD_SEQ}", "STATUS:CONFIRMED",
            f"DTSTART:{s['utc_s']}", f"DTEND:{s['utc_e']}", f"SUMMARY:{esc(T('ics_summary', n=s['n']))}",
            f"DESCRIPTION:{esc(desc)}", f"LOCATION:{esc(T('ics_loc'))}", f"URL:{page_url(s['n'])}",
            "BEGIN:VALARM","TRIGGER:-PT60M","ACTION:DISPLAY",f"DESCRIPTION:{esc(T('ics_alarm'))}","END:VALARM","END:VEVENT"]
def fold(line):
    """RFC 5545: linii de max. 75 octeți, continuare cu spațiu; nu taie caractere UTF-8"""
    out, cur, n = [], "", 0
    for ch in line:
        k = len(ch.encode("utf-8"))
        if n + k > (75 if not out else 74):
            out.append(cur); cur, n = "", 0
        cur += ch; n += k
    out.append(cur)
    return "\r\n ".join(out)
def ics(events):
    lines = ["BEGIN:VCALENDAR","VERSION:2.0",f"PRODID:-//ASFAN//Curs Ufologie 4//{CODE.upper()}","CALSCALE:GREGORIAN",f"X-WR-CALNAME:{esc(T('ics_cal'))}"]
    for ev in events: lines += vevent(ev)
    lines.append("END:VCALENDAR"); return "\r\n".join(fold(l) for l in lines) + "\r\n"
# ------------------------------------------------------------------ iconițe
IC = {
 "cal":'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="5" y="8" width="30" height="27" rx="3"/><path d="M5 16h30M12 4v8M28 4v8M11 22h4M18 22h4M25 22h4M11 28h4M18 28h4M25 28h4"/></svg>',
 "clock":'<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="15"/><path d="M20 10v10l7 5"/></svg>',
 "zoom":'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="3" y="9" width="34" height="22" rx="11" fill="#1d7bf0" stroke="#1d7bf0"/><path d="M12 15h10a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H12zM24 19l6-4v10l-6-4" fill="#fff" stroke="#fff"/></svg>',
 "ppl":'<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="14" cy="14" r="5"/><circle cx="27" cy="15" r="4"/><path d="M4 33c0-6 4-10 10-10s10 4 10 10M24 24c5-1 12 1 12 9"/></svg>',
 "gift":'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="5" y="15" width="30" height="7" rx="1"/><path d="M7 22v13h26V22M20 15v20M20 15c-3-8-11-6-8-1 1 1 5 1 8 1zM20 15c3-8 11-6 8-1-1 1-5 1-8 1z"/></svg>',
 "seats":'<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="12" r="5"/><circle cx="8" cy="15" r="4"/><circle cx="32" cy="15" r="4"/><path d="M10 33c0-7 4-11 10-11s10 4 10 11M2 30c0-5 2-8 6-9M38 30c0-5-2-8-6-9"/></svg>',
 "mail":'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="4" y="9" width="32" height="22" rx="3"/><path d="M5 11l15 12 15-12"/></svg>',
 "globe":'<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="16"/><path d="M4 20h32M20 4c-8 9-8 23 0 32M20 4c8 9 8 23 0 32"/></svg>',
}


# ------------------------------------------------------------------ layout
NAV = [("inv","nav_inv"),("plan","nav_program"),("inscriere","nav_enroll"),("qr","nav_qr")]
def lang_href(code, path):
    """link relativ către aceeași pagină în limba `code`"""
    if path == "index.html":
        if CODE == "ro": return "./" if code == "ro" else f"{code}/"
        return "../" if code == "ro" else ("./" if code == CODE else f"../{code}/")
    if CODE == "ro": return path if code == "ro" else f"{code}/{path}"
    return f"../{path}" if code == "ro" else (path if code == code and code == CODE else f"../{code}/{path}")
def loc_url(code, path):
    base = SITE + "/" + ("" if code == "ro" else code + "/")
    return base + ("" if path == "index.html" else path)

CURPATH = "index.html"
def head(title, desc, page, path, extra=""):
    global CURPATH
    CURPATH = path
    canon = loc_url(CODE, path)
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{loc_url(l, path)}">\n' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{loc_url("ro", path)}">\n'
    langlinks = "".join(f'<li><a lang="{l}" hreflang="{l}" data-lang-link="{l}" href="{lang_href(l, path)}"{" aria-current=\"true\"" if l == CODE else ""}>{E(DATA[l]["meta"]["name"])}</a></li>' for l in LANGS)
    navl = "".join(f'    <a class="lnk" data-sec="{h}" data-k="{k}" href="#{h}">{T(k)}</a>\n' for h, k in NAV)
    return f'''<!DOCTYPE html>
<html lang="{LD["meta"]["html_lang"]}" data-theme="moai">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc, quote=True)}">
<meta name="theme-color" content="#030a1c"><meta name="color-scheme" content="dark">
<link rel="canonical" href="{canon}">
{alts}<link rel="icon" href="{P}assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:locale" content="{LD["meta"]["locale"]}">
<meta property="og:title" content="{E(title, quote=True)}"><meta property="og:description" content="{E(desc, quote=True)}">
<meta property="og:url" content="{canon}"><meta property="og:site_name" content="ASFAN – curs.asfan.online"><meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{A("og_alt")}"><meta name="twitter:image:alt" content="{A("og_alt")}">
{"".join(f'<meta property="og:locale:alternate" content="{DATA[l]["meta"]["locale"]}">' for l in LANGS if l != CODE)}
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'; frame-src 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="twitter:card" content="summary_large_image">
<script>document.documentElement.classList.add('js');try{{var t=new URLSearchParams(location.search).get('tema')||localStorage.getItem('asfan-theme-v3');if(t==='anzi'||t==='moai')document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<link rel="preload" href="{P}assets/fonts/mont-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}assets/fonts/ss-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}assets/style.css?v={av("style.css")}">
{extra}
</head>
<body data-page="{page}">
<canvas id="stars" aria-hidden="true"></canvas>
<header class="topbar"><a class="skip" href="#main" data-k="skip">{T("skip")}</a><div class="wrap">
  <a class="brand" data-sec="top" data-k-aria="brand_aria" href="#top" aria-label="{A("brand_aria")}"><img src="{P}assets/logo.png" alt="{A("logo_alt")}" data-k-alt="logo_alt" width="108" height="40"><small data-k="brand_small">{T("brand_small")}</small></a>
  <details class="lang"><summary data-lang-aria aria-label="{CODE.upper()} – {A("lang_aria")}"><span aria-hidden="true">🌐</span> <b>{CODE.upper()}</b></summary><ul>{langlinks}</ul></details>
  <button class="btn-menu" type="button" aria-expanded="false" aria-controls="nav" data-k="menu_btn">{T("menu_btn")}</button>
  <nav class="main" id="nav" aria-label="{A("nav_aria")}" data-k-aria="nav_aria">
{navl}    <span class="theme-switch" role="group" aria-label="{A("theme_aria")}" data-k-aria="theme_aria">
      <button type="button" data-theme="moai" aria-pressed="true">🗿 Moai</button>
      <button type="button" data-theme="anzi" aria-pressed="false">🏔️ Anzi</button>
    </span>
  </nav>
</div></header>
<main id="main">
'''

def share_block():
    url = loc_url(CODE, CURPATH); txt = T("share_text"); ttl = T("title_index")
    from urllib.parse import quote as q
    nets = [("Facebook", "https://www.facebook.com/sharer/sharer.php?u=" + q(url, safe="")),
            ("X", "https://twitter.com/intent/tweet?url=" + q(url, safe="") + "&text=" + q(txt, safe="")),
            ("LinkedIn", "https://www.linkedin.com/sharing/share-offsite/?url=" + q(url, safe="")),
            ("WhatsApp", "https://wa.me/?text=" + q(txt + " " + url, safe="")),
            ("Telegram", "https://t.me/share/url?url=" + q(url, safe="") + "&text=" + q(txt, safe="")),
            ("E-mail", "mailto:?subject=" + q(ttl, safe="") + "&body=" + q(txt + "\n\n" + url, safe=""))]
    links = "".join(f'<a class="share-b" data-net="{n}" href="{E(h, quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{A("share_via", net=n)}">{n}</a>' for n, h in nets)
    return f'''<div class="wrap share" data-share data-share-url="{url}" data-share-title="{E(ttl, quote=True)}" data-share-text="{E(txt, quote=True)}">
    <span class="share-h" data-k="share_h">{T("share_h")}</span>
    <div class="share-btns"><button class="share-b share-native" type="button" hidden data-k="share_native">{T("share_native")}</button>{links}<button class="share-b" type="button" data-copy="{url}" data-copied="{JS("copied")}" data-k="share_copy">{T("share_copy")}</button></div>
  </div>'''

def foot():
    links = "".join(f'<a data-sec="{h}" data-k="{k}" href="#{h}">{T(k)}</a>' for h, k in NAV)
    return f'''</main>
<footer>
  <div class="foot-poster">
    <div class="foot-art" aria-hidden="true"><div class="foot-hand art-a" data-k="foot_hand">{T("foot_hand")}</div><div class="foot-hand art-b" data-k="foot_hand2">{T("foot_hand2")}</div></div>
    <div class="foot-bar"><div class="wrap">
      <a class="site" href="{ASFAN}" rel="noopener">{IC['globe']}<span>www.asfanufo.ro</span></a>
      <div class="tag"><b data-k="foot_tag_b">{T("foot_tag_b")}</b><small data-k="foot_tag_s">{T("foot_tag_s")}</small></div>
      <a class="foot-qr" data-sec="qr" data-k-aria="foot_qr_aria" href="#qr" aria-label="{A("foot_qr_aria")}"><img src="{P}assets/qr-curs.svg" width="64" height="64" alt="{A("foot_qr_alt")}" data-k-alt="foot_qr_alt"></a>
    </div></div>
  </div>
  {share_block()}
  <div class="wrap foot-links">{links}<a href="mailto:{MAIL}">{MAIL}</a></div>
</footer>
<script src="{P}assets/sessions.js?v={av("sessions.js")}"></script>
<script src="{P}assets/i18n-{CODE}.js?v={av(f"i18n-{CODE}.js")}"></script>
<script src="{P}assets/app.js?v={av("app.js")}"></script>
</body></html>'''

def write(path, content):
    open(f"{DIR}/{path}", "w", encoding="utf-8").write(content)

def qr_block():
    return f'''<div class="qrs">
  <div class="qr"><div class="code"><img src="{P}assets/qr-curs.svg" width="210" height="210" alt="{A("qr_alt", url=SITE + "/")}"></div>
    <div><h3>{T("qr_course_h")}</h3><p>{T("qr_course_p")}</p><div class="url">curs.asfan.online</div>
    <div class="acts"><a class="btn btn-blue" href="{P}assets/qr-curs.png" download="qr-curs-asfan-online.png">PNG</a><a class="btn btn-ghost" href="{P}assets/qr-curs.svg" download="qr-curs-asfan-online.svg">SVG</a><button class="btn btn-ghost" type="button" data-copy="{SITE}/" data-copied="{JS("copied")}">{T("qr_copy")}</button></div></div></div>
  <div class="qr"><div class="code"><img src="{P}assets/qr-asfan.svg" width="210" height="210" alt="{A("qr_alt", url=ASFAN)}"></div>
    <div><h3>{T("qr_asfan_h")}</h3><p>{T("qr_asfan_p")}</p><div class="url">www.asfanufo.ro</div>
    <div class="acts"><a class="btn btn-blue" href="{P}assets/qr-asfan.png" download="qr-asfanufo-ro.png">PNG</a><a class="btn btn-ghost" href="{P}assets/qr-asfan.svg" download="qr-asfanufo-ro.svg">SVG</a><button class="btn btn-ghost" type="button" data-copy="{ASFAN}" data-copied="{JS("copied")}">{T("qr_copy")}</button></div></div></div>
</div>'''

def notice():
    if CODE == "ro": return ""
    return f'<div class="lang-note" role="note"><div class="wrap"><span aria-hidden="true">🇷🇴</span> <span data-k="lang_notice">{T("lang_notice")}</span></div></div>\n'

def crumbs(*items):
    return '<div class="crumbs">' + f'<a href="index.html">{T("crumb_home")}</a>' + "".join(" › " + i for i in items) + '</div>'

# ------------------------------------------------------------------ pagina unică
RO_SUBJECT = "Înscriere curs „Introducere în ufologie” (seria a patra)"
RO_BODY = ("Bună ziua,\n\nDoresc să mă înscriu la cursul „Introducere în ufologie” (seria a patra), organizat de ASFAN, "
           "18 noiembrie 2026 – 26 mai 2027, prin ZOOM.\n\nNume și prenume: \nAdresa de e-mail pentru link-urile ZOOM: \nLocalitatea: \n\n"
           "Înțeleg că participarea este gratuită, că locurile sunt limitate și că diploma se poate solicita cu cel mult trei absențe.\n\nMulțumesc!\n")
def mailto_href():
    from urllib.parse import quote as q
    return "mailto:" + MAIL + "?subject=" + q(RO_SUBJECT, safe="") + "&body=" + q(RO_BODY.replace("\n", "\r\n"), safe="")

def events_ld():
    ev = [{"@type":"Event","name":f"{T('ld_name')} – {x['n']}/14","description":x["text"],"startDate":x["start"],"endDate":x["end"],"inLanguage":"ro",
           "eventStatus":"https://schema.org/EventScheduled","eventAttendanceMode":"https://schema.org/OnlineEventAttendanceMode",
           "location":{"@type":"VirtualLocation","url":SITE + "/"},"isAccessibleForFree":True,
           "organizer":{"@type":"Organization","name":"ASFAN","url":ASFAN},"performer":{"@type":"Person","name":"Dan D. Farcaș"},
           "offers":{"@type":"Offer","price":"0","priceCurrency":"RON","availability":"https://schema.org/LimitedAvailability","url":SITE + "/"}} for x in SESS]
    return '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@graph":ev}, ensure_ascii=False) + '</script>'

def gmail_href():
    from urllib.parse import quote as q
    return "https://mail.google.com/mail/?view=cm&fs=1&to=" + MAIL + "&su=" + q(RO_SUBJECT, safe="") + "&body=" + q(RO_BODY, safe="")

def page_index():
    h = head(T("title_index"), T("desc_index"), "index", "index.html",
             '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"Course","name":T("ld_name"),"inLanguage":"ro","availableLanguage":["ro"],
              "description":T("ld_desc"),"provider":{"@type":"Organization","name":"ASFAN","sameAs":ASFAN},
              "hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","startDate":"2026-11-18","endDate":"2027-05-26","instructor":{"@type":"Person","name":"Dan D. Farcaș"}},
              "offers":{"@type":"Offer","price":"0","priceCurrency":"RON"},"url":loc_url(CODE, "index.html")}, ensure_ascii=False) + '</script>' + events_ld())
    MT = mailto_href(); GM = gmail_href()
    full_msg = "To: " + MAIL + "\nSubject: " + RO_SUBJECT + "\n\n" + RO_BODY
    tz = f'<p class="tz-note">🕖 {T("tz_note")}</p>' if T("tz_note") else ""
    tags = "<i>•</i>".join(f"<span>{E(x)}</span>" for x in UI["hero_tags"].split("|"))
    mini = "".join(f"<span>{E(x)}</span>" for x in UI["mini_tags"].split("|"))
    topics = "".join(f'''      <div class="topic"><img class="art-a" src="{P}assets/a-t{i}.jpg" alt="" width="170" height="52" loading="lazy"><img class="art-b" src="{P}assets/b-t{i}.jpg" alt="" width="170" height="52" loading="lazy"><div><h3>{E(t)}</h3><p>{E(s)}</p></div></div>
''' for i, (t, s) in enumerate(LD["topics"], 1))
    plan = "".join(f'''      <li id="s{x["n"]}"><time datetime="{x["date"].isoformat()}"><b>{E(x["label"])}</b><span>19:00–21:00</span></time>
        <p>{E(x["text"])}</p>
        <a class="ics" href="{P}{CAL}sesiune-{x["n"]}.ics" data-ics="sesiune-{x["n"]}" download aria-label="{A("plan_ics")} – {E(x["label"], quote=True)}">📅 <span>{T("plan_ics")}</span></a></li>
''' for x in SESS)
    conds = "".join(f"<li>{E(x)}</li>" for x in UI["enr_cond"].split("|"))
    poster_block = f'''<div class="pst" id="top">
<section class="hero">
  <img class="hero-art art-a art-left" src="{P}assets/a-moai.jpg" alt="" width="126" height="176">
  <img class="hero-art art-b art-left" src="{P}assets/b-machu.jpg" alt="" width="330" height="236">
  <img class="hero-art art-a art-ufo" src="{P}assets/a-ufo.jpg" alt="" width="240" height="117">
  <img class="hero-art art-b art-ufo" src="{P}assets/b-ufo.jpg" alt="" width="297" height="98">
  <div class="hand hand-l" aria-hidden="true">{T("hand_l")}</div>
  <div class="hand hand-r" aria-hidden="true">{T("hand_r")}<span class="sw"></span></div>
  <div class="wrap hero-inner">
    <div class="hero-logo"><a class="logo-home" data-sec="top" href="#top" aria-label="{A("brand_aria")}" data-k-aria="brand_aria"><img src="{P}assets/logo.png" alt="{A("logo_alt")}" data-k-alt="logo_alt" width="163" height="105"></a>
      <div class="motto">{T("motto")}<div class="about">{T("about_assoc")}</div></div></div>
    <div class="hero-center">
      <div class="hero-title">
        <p class="t-sub">{T("hero_sub")}</p>
        <h1 class="t-main"><span class="vh">{E(UI["hero_h1_pre"])}</span>{E(UI["hero_main"])}<span class="vh">{E(UI["hero_h1_post"])}</span></h1>
        <p class="t-curs">{T("hero_curs")}</p>
        <p class="t-serie">{T("hero_serie")}</p>
      </div>
      <div class="hero-info">
        <p class="t-date">{T("hero_date")}</p>
        <p class="t-line">{T("hero_line")}</p>
        <div class="tags">{tags}</div>
      </div>
      <div class="hero-cta"><a class="btn btn-gold" href="#inscriere" data-sec="inscriere">{T("cta_enroll")}</a><a class="btn btn-ghost" data-sec="plan" href="#plan">{T("cta_program")}</a></div>
      <div class="mini-tags" aria-hidden="true">{mini}</div>
    </div>
    <div class="coord">
      <div class="ph ph-a"><img src="{P}assets/a-portrait.jpg" alt="Dan D. Farcaș" width="246" height="288"></div>
      <div class="ph art-b-ph"><img src="{P}assets/b-portrait.jpg" alt="Dan D. Farcaș" width="244" height="252"></div>
      <div class="who"><b>Dan D. Farcaș</b><span>{T("coord_role1")}</span><span>{T("coord_role2")}</span></div>
    </div>
  </div>
</section>
<div class="wrap pst-body">
  <div class="cards4">
    <div class="ic">{IC['cal']}<div><p class="ict">{T("card_when")}</p><strong>{T("card_when_v")}</strong><span class="sm">{T("card_when_n")}</span></div></div>
    <div class="ic">{IC['clock']}<div><p class="ict">{T("card_time")}</p><strong>{T("card_time_v")}</strong><span class="sm sm2">{T("card_time_n")}</span></div></div>
    <div class="ic">{IC['zoom']}<div><p class="ict">{T("card_where")}</p><strong>{T("card_where_v")}</strong></div></div>
    <div class="ic">{IC['ppl']}<div><p class="ict">{T("card_who")}</p><span class="sm sm4">{T("card_who_v")}</span></div></div>
  </div>
  <section class="sec" aria-labelledby="h-st">
    <h2 id="h-st">{T("h_study")} <span class="sub">{T("h_study_sub")}</span></h2>
    <div class="topics">
{topics}    </div>
  </section>
  <div class="boxes">
    <div class="box free"><h3>{IC['gift']}<span>{T("box_free_t")}</span></h3><p>{T("box_free_p")}</p></div>
    <div class="box seats"><h3>{IC['seats']}<span>{T("box_seats_t")}</span></h3><p>{T("box_seats_p")}</p></div>
    <div class="box enroll"><h3>{IC['mail']}<a class="ttl" href="#inscriere" data-sec="inscriere">{T("box_enroll_t")}</a></h3><p>{T("box_enroll_p")}</p></div>
  </div>
</div>
</div>
'''
    compact_block = f'''<div class="wrap page-head top-compact" id="top">
  <p class="kick">{T("about_assoc")}</p>
  <h1>{E(UI["hero_h1_pre"])}<em>{E(UI["hero_main"])}</em></h1>
  <p class="lead"><b>{T("hero_curs")}</b> {T("hero_serie")} · {T("hero_date")}</p>
  <p class="lead sm-l">{T("hero_line")}</p>
  <div class="tags">{tags}</div>
  <p class="who-l"><b>Dan D. Farcaș</b> – {T("coord_role1")}, {T("coord_role2")}</p>
  <p class="top-cta"><a class="btn btn-gold" href="#inscriere" data-sec="inscriere">{T("cta_enroll")}</a></p>
  <ul class="enr-conds facts"><li>📅 {T("card_when_v")}</li><li>🕖 {T("card_time_v")}</li><li>💻 {T("card_where_v")}</li><li>🎁 {T("box_free_t")}</li><li>👥 {T("box_seats_t")}</li></ul>
  {tz}
</div>
'''
    top_block = poster_block if POSTER else compact_block
    acs = "".join(f'''    <details class="ac" id="s{x["n"]}" data-sess="{x["n"]}" open>
      <summary><span class="num">{x["n"]}</span><h3 class="sh"><span class="dt">{x["label"]} · 19:00–21:00</span>{"" if SIMPLE else '<span class="tt">' + E(x["title"]) + '</span>'}</h3></summary>
      <div class="body"><p>{E(x["text"])}</p>
        {"" if SIMPLE else '<ul class="chips">' + "".join(f"<li>{E(c)}</li>" for c in x["chips"]) + '</ul>'}
        <p style="margin-top:14px"><a class="btn btn-ghost" href="{P}{CAL}sesiune-{x["n"]}.ics" data-ics="sesiune-{x["n"]}" download>{T("prog_cal")}</a></p></div>
    </details>
''' for x in SESS)
    plan_block = f'''<section class="doc plan" id="plan" aria-labelledby="h-plan">
  <div class="wrap">
    <header class="page-head"><h2 id="h-plan">{T("prog_h1")}</h2><p class="lead">{T("prog_lead")}</p></header>
    <div class="toolbar">
      <button class="btn btn-blue expand-all" type="button" data-expand="{JS("expand")}" data-collapse="{JS("collapse")}">{JS("collapse")}</button>
      <a class="btn btn-gold" href="{P}{CAL}curs-complet.ics" data-ics="curs-complet" download>{T("prog_cal_all")}</a>
      <input class="sess-filter" type="search" placeholder="{A("prog_filter_ph")}" aria-label="{A("prog_filter_aria")}">
    </div>
{acs}    <p class="no-res" role="status" hidden>{T("prog_none")}</p>
    <p class="note">{T("prog_note")}</p>
  </div>
</section>'''
    b = notice() + f'''<div class="course-over-note" role="note" data-k="over_note">{T("over_note")}</div>
<div class="count slim" data-next-wrap><div class="wrap"><span class="lbl" data-next-label>{T("cd_start", label=SESS[0]["label"])}</span>
    <div class="cd" data-next-cd data-countdown="2026-11-18T19:00:00+02:00" data-done="{JS("started")}" aria-live="off"></div><a class="btn btn-gold bar-cta" href="#inscriere" data-sec="inscriere">{T("nav_enroll")}</a></div></div>
{top_block}

<section class="doc" id="inv" aria-labelledby="h-inv">
  <div class="wrap">
    <article class="letter">
      <p class="l-org">{T("about_assoc")} (ASFAN)</p>
      <h2 id="h-inv" class="l-h">{T("inv_h")}</h2>
      <p class="l-lead">{T("inv_lead")}</p>
      <p class="l-title">{T("inv_title")}</p>
      <p class="l-serie">{T("hero_serie")}</p>
      <p>{T("about_p1")}</p>
      <p>{T("about_p2")}</p>
      <p>{T("about_p3")}</p>
      <p>{T("about_p4")}</p>
      <p class="l-sign">{T("inv_sign")},<br><b>Dan D. Farcaș</b></p>
    </article>
  </div>
</section>

{plan_block}

<section class="doc enroll-sec" id="inscriere" aria-labelledby="h-enr">
  <div class="wrap">
    <div class="enr-card">
      <h2 id="h-enr">{T("enr_h1")}</h2>
      <p class="lead">{T("enr_lead")}</p>
      <div class="count"><span class="lbl">{T("enr_cd_label")}</span><div class="cd" data-countdown="2026-11-17T23:59:59+02:00" data-done="{A("enr_cd_done")}"></div></div>
      <ul class="enr-conds">{conds}</ul>
      <p class="enr-act"><a class="btn btn-gold btn-lg" href="{MT}" data-mail>{T("enr_btn")}</a></p>
      <p class="note">{T("enr_hint")}</p>
      <p class="enr-alt"><span>{T("enr_alt")}</span> <a class="btn btn-ghost btn-sm" href="{GM}" target="_blank" rel="noopener noreferrer">{T("enr_gmail")}</a> <button class="btn btn-ghost btn-sm" type="button" data-copy="{E(full_msg, quote=True)}" data-copied="{JS("copied")}">{T("enr_copy_msg")}</button></p>
      <p class="note">{T("enr_write")} <a href="mailto:{MAIL}"><b>{MAIL}</b></a> <button class="btn btn-ghost btn-sm" type="button" data-copy="{MAIL}" data-copied="{JS("copied")}">{T("enr_copy_addr")}</button></p>
    </div>
  </div>
</section>

<section class="doc qr-sec" id="qr" aria-labelledby="h-qr">
  <div class="wrap">
    <h2 id="h-qr">{T("qr_h1")}</h2>
    <p class="lead">{T("qr_lead")}</p>
    {qr_block()}
  </div>
</section>
'''
    return h + b + foot()

# ------------------------------------------------------------------ scriere
for CODE in LANGS:
    LD = DATA[CODE]; UI = LD["ui"]; SESS = build_sess()
    P = "" if CODE == "ro" else "../"
    CAL = "calendar/" if CODE == "ro" else f"calendar/{CODE}/"
    DIR = OUT if CODE == "ro" else f"{OUT}/{CODE}"
    os.makedirs(DIR, exist_ok=True); os.makedirs(f"{OUT}/{CAL}", exist_ok=True)
    for s in SESS: open(f"{OUT}/{CAL}sesiune-{s['n']}.ics","w",encoding="utf-8",newline="").write(ics([s]))
    open(f"{OUT}/{CAL}curs-complet.ics","w",encoding="utf-8",newline="").write(ics(SESS))
    if CODE == "ro":   # date independente de limbă
        open(f"{OUT}/assets/sessions.js","w",encoding="utf-8").write("window.ASFAN_SESSIONS="+json.dumps([dict(n=s["n"],start=s["start"],end=s["end"]) for s in SESS])+";\n")
    chrome = {k: UI[k] for k in ("skip","brand_aria","brand_small","logo_alt","menu_btn","nav_aria","nav_home","nav_program","nav_about","nav_enroll","nav_qr","theme_aria","lang_aria",
              "nav_inv","over_note","lb_aria","lb_dl","lb_close","lb_alt","foot_hand","foot_hand2","foot_tag_b","foot_tag_s","foot_qr_aria","foot_qr_alt","share_h","share_native","share_copy","share_via","share_text","lang_notice")}
    open(f"{OUT}/assets/i18n-{CODE}.js","w",encoding="utf-8").write("window.ASFAN_I18N="+json.dumps(dict(lang=CODE,js=LD["js"],labels=[s["label"] for s in SESS],chrome=chrome,
        titles={"index":UI["title_index"]},
        cd_start=UI["cd_start"]),ensure_ascii=False)+";\n")
    write("index.html", page_index())
    base = SITE + "/" + ("" if CODE == "ro" else CODE + "/")
    olds = {"program.html":"#plan","detalii.html":"#inv","inscriere.html":"#inscriere","qr.html":"#qr"}
    olds.update({f"sesiune-{i}.html": f"#s{i}" for i in range(1, 15)})
    for fn, anc in olds.items():
        write(fn, f'''<!DOCTYPE html>
<html lang="{LD["meta"]["html_lang"]}"><head><meta charset="utf-8"><title>{E(UI["title_index"])}</title><meta name="robots" content="noindex">
<link rel="canonical" href="{base}"><meta http-equiv="refresh" content="0;url={base}{anc}">
<script>location.replace("{base}{anc}")</script></head>
<body><p><a href="{base}{anc}">{E(UI["title_index"])}</a></p></body></html>
''')

open(f"{OUT}/CNAME","w").write("curs.asfan.online\n")
open(f"{OUT}/404.html","w",encoding="utf-8").write(f'''<!DOCTYPE html>
<html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pagina nu există · curs.asfan.online</title><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url={SITE}/"><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#030a1c;color:#eaf2ff;font-family:system-ui,sans-serif;text-align:center;padding:20px}}a{{color:#f7b733;font-weight:700}}</style></head>
<body><main><h1>Pagina nu a fost găsită</h1><p>Te ducem la pagina cursului „Introducere în ufologie”…</p><p><a href="{SITE}/">curs.asfan.online</a></p></main></body></html>
''')
open(f"{OUT}/assets/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#06142f"/><ellipse cx="32" cy="30" rx="24" ry="8" fill="#4cc9ff"/><ellipse cx="32" cy="26" rx="11" ry="9" fill="#bfe6ff"/><path d="M22 38l-6 14h32l-6-14z" fill="#f7b733" opacity=".55"/></svg>')
open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nDisallow: /src/\nSitemap: {SITE}/sitemap.xml\n")
pages = ["index.html"]
def alt(p): return "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{loc_url(l, p)}"/>' for l in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{loc_url("ro", p)}"/>'
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "".join(f"<url><loc>{loc_url(l, p)}</loc><lastmod>{dt.date.today().isoformat()}</lastmod>{alt(p)}</url>\n" for p in pages for l in LANGS) + "</urlset>\n")
print("OK", len(LANGS), "limbi;", len(pages) * len(LANGS), "pagini")
