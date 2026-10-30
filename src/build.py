#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generează site-ul static multilingv curs.asfan.online în ./site (ro la rădăcină, celelalte limbi în ./site/<cod>/)"""
import os, json, html, datetime as dt, shutil
import segno

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(ROOT)   # rădăcina depozitului = site-ul servit
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
    q.save(f"{OUT}/assets/{name}.svg", scale=10, border=2, dark="#06142f", light="#ffffff", xmldecl=False, svgns=True)
    q.save(f"{OUT}/assets/{name}.png", scale=24, border=3, dark="#06142f", light="#ffffff")
make_qr(SITE + "/", "qr-curs"); make_qr(ASFAN, "qr-asfan")

# ------------------------------------------------------------------ ICS (per limbă)
def esc(s): return s.replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
def page_url(n): return SITE + "/" + (CODE + "/" if CODE != "ro" else "") + f"sesiune-{n}.html"
def vevent(s):
    desc = f"{s['title']}\n\n{s['text']}\n\n" + T("ics_desc", url=page_url(s['n']))
    return ["BEGIN:VEVENT", f"UID:asfan-ufologie-4-s{s['n']}-{CODE}@curs.asfan.online", "DTSTAMP:20261030T000000Z",
            f"DTSTART:{s['utc_s']}", f"DTEND:{s['utc_e']}", f"SUMMARY:{esc(T('ics_summary', n=s['n']))}",
            f"DESCRIPTION:{esc(desc)}", f"LOCATION:{esc(T('ics_loc'))}", f"URL:{page_url(s['n'])}",
            "BEGIN:VALARM","TRIGGER:-PT60M","ACTION:DISPLAY",f"DESCRIPTION:{esc(T('ics_alarm'))}","END:VALARM","END:VEVENT"]
def ics(events):
    lines = ["BEGIN:VCALENDAR","VERSION:2.0",f"PRODID:-//ASFAN//Curs Ufologie 4//{CODE.upper()}","CALSCALE:GREGORIAN",f"X-WR-CALNAME:{esc(T('ics_cal'))}"]
    for ev in events: lines += vevent(ev)
    lines.append("END:VCALENDAR"); return "\r\n".join(lines) + "\r\n"
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
NAV = [("index.html","nav_home",""),("program.html","nav_program","program"),("detalii.html","nav_about","detalii"),("inscriere.html","nav_enroll","inscriere"),("qr.html","nav_qr","qr")]
def lang_href(code, path):
    """link relativ către aceeași pagină în limba `code`"""
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
    navl = "".join(f'    <a class="lnk" data-nav="{r}" data-k="{k}" href="{h}"{" aria-current=\"page\"" if h == path else ""}>{T(k)}</a>\n' for h, k, r in NAV)
    return f'''<!DOCTYPE html>
<html lang="{LD["meta"]["html_lang"]}" data-theme="anzi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc, quote=True)}">
<meta name="theme-color" content="#0b1b3b"><meta name="color-scheme" content="dark">
<link rel="canonical" href="{canon}">
{alts}<link rel="icon" href="{P}assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:locale" content="{LD["meta"]["locale"]}">
<meta property="og:title" content="{E(title, quote=True)}"><meta property="og:description" content="{E(desc, quote=True)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<script>document.documentElement.classList.add('js');try{{var t=new URLSearchParams(location.search).get('tema')||localStorage.getItem('asfan-theme-v2');if(t==='anzi'||t==='moai')document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<link rel="stylesheet" href="{P}assets/style.css">
{extra}
</head>
<body data-page="{page}">
<canvas id="stars" aria-hidden="true"></canvas>
<header class="topbar"><a class="skip" href="#main" data-k="skip">{T("skip")}</a><div class="wrap">
  <a class="brand" data-nav="" data-k-aria="brand_aria" href="index.html" aria-label="{A("brand_aria")}"><img src="{P}assets/logo.png" alt="{A("logo_alt")}" data-k-alt="logo_alt" width="108" height="40"><small data-k="brand_small">{T("brand_small")}</small></a>
  <details class="lang"><summary data-k-aria="lang_aria" aria-label="{A("lang_aria")}"><span aria-hidden="true">🌐</span> <b>{CODE.upper()}</b></summary><ul>{langlinks}</ul></details>
  <button class="btn-menu" type="button" aria-expanded="false" aria-controls="nav" data-k="menu_btn">{T("menu_btn")}</button>
  <nav class="main" id="nav" aria-label="{A("nav_aria")}" data-k-aria="nav_aria">
{navl}    <span class="theme-switch" role="group" aria-label="{A("theme_aria")}" data-k-aria="theme_aria">
      <button type="button" data-theme="moai" aria-pressed="false">🗿 Moai</button>
      <button type="button" data-theme="anzi" aria-pressed="true">🏔️ Anzi</button>
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
    links = "".join(f'<a data-nav="{r}" data-k="{k}" href="{h}">{T(k)}</a>' for h, k, r in NAV[1:])
    return f'''</main>
<dialog id="lb" aria-label="{A("lb_aria")}" data-k-aria="lb_aria"><div class="in"><div class="bar"><a class="btn btn-gold dl" href="#" download data-k="lb_dl">{T("lb_dl")}</a><button class="btn btn-ghost close" type="button" data-k="lb_close">{T("lb_close")}</button></div><img alt="{A("lb_alt")}" data-k-alt="lb_alt" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></div></dialog>
<footer>
  <div class="foot-poster">
    <div class="foot-art" aria-hidden="true"><div class="foot-hand art-a" data-k="foot_hand">{T("foot_hand")}</div><div class="foot-hand art-b" data-k="foot_hand2">{T("foot_hand2")}</div></div>
    <div class="foot-bar"><div class="wrap">
      <a class="site" href="{ASFAN}" rel="noopener">{IC['globe']}<span>www.asfanufo.ro</span></a>
      <div class="tag"><b data-k="foot_tag_b">{T("foot_tag_b")}</b><small data-k="foot_tag_s">{T("foot_tag_s")}</small></div>
      <a class="foot-qr" data-nav="qr" data-k-aria="foot_qr_aria" href="qr.html" aria-label="{A("foot_qr_aria")}"><img src="{P}assets/qr-curs.svg" width="64" height="64" alt="{A("foot_qr_alt")}" data-k-alt="foot_qr_alt"></a>
    </div></div>
  </div>
  {share_block()}
  <div class="wrap foot-links">{links}<a href="mailto:{MAIL}">{MAIL}</a></div>
</footer>
<script src="{P}assets/sessions.js"></script>
<script src="{P}assets/i18n-{CODE}.js"></script>
<script src="{P}assets/app.js"></script>
</body></html>'''

def write(path, content):
    open(f"{DIR}/{path}", "w", encoding="utf-8").write(content)

def qr_block():
    return f'''<div class="qrs">
  <div class="qr"><div class="code"><img src="{P}assets/qr-curs.svg" width="150" height="150" alt="{A("qr_alt", url=SITE + "/")}" loading="lazy"></div>
    <div><h2>{T("qr_course_h")}</h2><p>{T("qr_course_p")}</p><div class="url">curs.asfan.online</div>
    <div class="acts"><a class="btn btn-blue" href="{P}assets/qr-curs.png" download="qr-curs-asfan-online.png">PNG</a><a class="btn btn-ghost" href="{P}assets/qr-curs.svg" download="qr-curs-asfan-online.svg">SVG</a><button class="btn btn-ghost" type="button" data-copy="{SITE}/" data-copied="{JS("copied")}">{T("qr_copy")}</button></div></div></div>
  <div class="qr"><div class="code"><img src="{P}assets/qr-asfan.svg" width="150" height="150" alt="{A("qr_alt", url=ASFAN)}" loading="lazy"></div>
    <div><h2>{T("qr_asfan_h")}</h2><p>{T("qr_asfan_p")}</p><div class="url">www.asfanufo.ro</div>
    <div class="acts"><a class="btn btn-blue" href="{P}assets/qr-asfan.png" download="qr-asfanufo-ro.png">PNG</a><a class="btn btn-ghost" href="{P}assets/qr-asfan.svg" download="qr-asfanufo-ro.svg">SVG</a><button class="btn btn-ghost" type="button" data-copy="{ASFAN}" data-copied="{JS("copied")}">{T("qr_copy")}</button></div></div></div>
</div>'''

def notice():
    if CODE == "ro": return ""
    return f'<div class="lang-note" role="note"><div class="wrap"><span aria-hidden="true">🇷🇴</span> <span data-k="lang_notice">{T("lang_notice")}</span></div></div>\n'

def crumbs(*items):
    return '<div class="crumbs">' + f'<a href="index.html">{T("crumb_home")}</a>' + "".join(" › " + i for i in items) + '</div>'

# ------------------------------------------------------------------ index
def page_index():
    h = head(T("title_index"), T("desc_index"), "index", "index.html",
             '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"Course","name":T("ld_name"),"inLanguage":"ro","availableLanguage":["ro"],
              "description":T("ld_desc"),"provider":{"@type":"Organization","name":"ASFAN","sameAs":ASFAN},
              "hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","startDate":"2026-11-18","endDate":"2027-05-26","instructor":{"@type":"Person","name":"Dan D. Farcaș"}},
              "offers":{"@type":"Offer","price":"0","priceCurrency":"RON"},"url":loc_url(CODE, "index.html")}, ensure_ascii=False) + '</script>')
    tags = "<i>•</i>".join(f"<span>{E(x)}</span>" for x in UI["hero_tags"].split("|"))
    mini = "".join(f"<span>{E(x)}</span>" for x in UI["mini_tags"].split("|"))
    topics = "".join(f'''      <a class="topic" href="sesiune-{TOPIC_SESS[i]}.html"><img class="art-a" src="{P}assets/a-t{i}.jpg" alt="" width="170" height="52" loading="lazy"><img class="art-b" src="{P}assets/b-t{i}.jpg" alt="" width="170" height="52" loading="lazy"><div><h3>{E(t)}</h3><p>{E(s)}</p></div><span class="go" aria-hidden="true">›</span></a>
''' for i, (t, s) in enumerate(LD["topics"], 1))
    b = notice() + f'''<div class="count slim" data-next-wrap><div class="wrap"><span class="lbl" data-next-label>{T("cd_start", label=SESS[0]["label"])}</span>
    <div class="cd" data-next-cd data-countdown="2026-11-18T19:00:00+02:00" data-done="{JS("started")}" aria-live="off"></div></div></div>
<div class="pst">
<section class="hero">
  <img class="hero-art art-a art-left" src="{P}assets/a-moai.jpg" alt="" width="126" height="176">
  <img class="hero-art art-b art-left" src="{P}assets/b-machu.jpg" alt="" width="330" height="236">
  <img class="hero-art art-a art-ufo" src="{P}assets/a-ufo.jpg" alt="" width="240" height="117">
  <img class="hero-art art-b art-ufo" src="{P}assets/b-ufo.jpg" alt="" width="297" height="98">
  <div class="hand hand-l" aria-hidden="true">{T("hand_l")}</div>
  <div class="hand hand-r" aria-hidden="true">{T("hand_r")}<span class="sw"></span></div>
  <div class="wrap hero-inner">
    <div class="hero-logo"><a class="logo-home" data-nav="" href="index.html" aria-label="{A("brand_aria")}" data-k-aria="brand_aria"><img src="{P}assets/logo.png" alt="{A("logo_alt")}" data-k-alt="logo_alt" width="163" height="105"></a>
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
      <div class="hero-cta"><a class="btn btn-gold" href="inscriere.html">{T("cta_enroll")}</a><a class="btn btn-ghost" href="program.html">{T("cta_program")}</a></div>
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
    <div class="box enroll"><h3>{IC['mail']}<a class="ttl" href="inscriere.html">{T("box_enroll_t")}</a></h3><p>{T("box_enroll_p")}</p></div>
  </div>
</div>
</div>
'''
    return h + b + foot()

# ------------------------------------------------------------------ program
def page_program():
    h = head(T("title_program"), T("desc_program"), "program", "program.html")
    b = notice() + f'''<div class="wrap">
  <div class="page-head">{crumbs(T("nav_program"))}
    <h1>{T("prog_h1")}</h1>
    <p class="lead">{T("prog_lead")}</p></div>
  <div class="toolbar">
    <button class="btn btn-blue expand-all" type="button" data-expand="{JS("expand")}" data-collapse="{JS("collapse")}">{T("prog_expand")}</button>
    <a class="btn btn-gold" href="{P}{CAL}curs-complet.ics" data-ics="curs-complet" download>{T("prog_cal_all")}</a>
    <input class="sess-filter" type="search" placeholder="{A("prog_filter_ph")}" aria-label="{A("prog_filter_aria")}" style="flex:1 1 240px;font:inherit;color:var(--txt);background:rgba(2,8,24,.85);border:1.5px solid var(--line);border-radius:999px;padding:11px 16px;min-height:46px">
  </div>
'''
    for s in SESS:
        b += f'''  <details class="ac reveal" id="s{s["n"]}" data-sess="{s["n"]}">
    <summary><span class="num">{s["n"]}</span><span><span class="dt">{s["label"]} · 19:00–21:00</span><br><span class="tt">{E(s["title"])}</span></span></summary>
    <div class="body"><p>{E(s["text"])}</p>
      <ul class="chips">{"".join(f"<li>{E(c)}</li>" for c in s["chips"])}</ul>
      <p style="margin-top:14px"><a class="btn btn-ghost" href="sesiune-{s["n"]}.html">{T("prog_session_page")}</a> <a class="btn btn-ghost" href="{P}{CAL}sesiune-{s["n"]}.ics" data-ics="sesiune-{s["n"]}" download>{T("prog_cal")}</a></p></div>
  </details>
'''
    b += f'''  <p class="note">{T("prog_note")}</p>
</div>
'''
    return h + b + foot()

# ------------------------------------------------------------------ session pages
def trunc(t, n=34): return E(t if len(t) <= n else t[:n].rstrip(" ,;:–-") + "…")
def page_session(s):
    n = s["n"]
    prv = SESS[n-2] if n > 1 else None
    nxt = SESS[n] if n < len(SESS) else None
    ttl = T("title_session", n=n, title=s["title"])
    if len(ttl) > 67: ttl = ttl[:66].rstrip(" ,;:–-") + "…"
    h = head(ttl, T("desc_session", label=s["label"], text=s["text"]), "sesiune", f"sesiune-{n}.html")
    rel = "".join(f'<li><a href="index.html#h-st" style="color:inherit;text-decoration:none">{E(LD["topics"][t-1][0])}</a></li>' for t in s["topics"])
    b = notice() + f'''<div class="wrap">
  <div class="page-head">{crumbs(f'<a href="program.html">{T("nav_program")}</a>', T("s_crumb", n=n))}
    <h1><em>{n:02d}.</em> {E(s["title"])}</h1>
    <p class="lead">{T("s_lead", label=s["label"])}</p></div>
  <div class="facts" data-sess="{n}">
    <div class="fact"><small>{T("fact_date")}</small><b>{s["label"]}</b></div>
    <div class="fact"><small>{T("fact_time")}</small><b>19:00 – 21:00</b></div>
    <div class="fact"><small>{T("fact_format")}</small><b>{T("s_format_v")}</b></div>
    <div class="fact"><small>{T("fact_place")}</small><b>{T("s_place_v")}</b></div>
  </div>
  <div class="count"><span class="lbl">{T("s_cd_label")}</span><div class="cd" data-countdown="{s["start"]}" data-done="{A("s_cd_done")}"></div></div>
  <div class="grid2" style="margin-top:20px">
    <div>
      <section class="panel"><h2 style="margin-top:0">{T("s_about")}</h2><p style="font-size:1.05rem">{E(s["text"])}</p>
        <ul class="chips">{"".join(f"<li>{E(c)}</li>" for c in s["chips"])}</ul></section>
      <section class="panel" style="margin-top:16px"><h2 style="margin-top:0">{T("s_topics")}</h2><ul>{rel}</ul></section>
      <p style="margin-top:16px"><a class="btn btn-gold" href="{P}{CAL}sesiune-{n}.ics" data-ics="sesiune-{n}" download>{T("s_add_cal")}</a> <a class="btn btn-blue" href="inscriere.html">{T("s_enroll")}</a></p>
      <p class="note">{T("s_note")}</p>
    </div>
    <aside class="panel sess-list" aria-label="{A("s_all")}"><h2 style="margin-top:0;font-size:1.2rem">{T("s_all")}</h2>
''' + "".join(f'      <a href="sesiune-{x["n"]}.html"{" aria-current=\"page\"" if x["n"]==n else ""}><b>{x["short"]}</b><span>{E(x["title"])}</span></a>\n' for x in SESS) + '''    </aside>
  </div>
  <div class="pager">
'''
    b += f'    <a class="btn btn-ghost" href="sesiune-{prv["n"]}.html">← {prv["n"]}. {trunc(prv["title"])}</a>\n' if prv else '    <span></span>\n'
    b += f'    <a class="btn btn-ghost" href="sesiune-{nxt["n"]}.html">{nxt["n"]}. {trunc(nxt["title"])} →</a>\n' if nxt else '    <span></span>\n'
    b += '  </div>\n</div>\n'
    return h + b + foot()

# ------------------------------------------------------------------ detalii
def page_detalii():
    h = head(T("title_about"), T("desc_about"), "detalii", "detalii.html")
    b = notice() + f'''<div class="wrap">
  <div class="page-head">{crumbs(T("nav_about"))}
    <h1>{T("about_h1")}</h1>
    <p class="lead">{T("about_lead")}</p></div>
  <div class="grid2">
    <section class="panel"><h2 style="margin-top:0">{T("about_invite")}</h2>
      <p>{T("about_p1")}</p>
      <p>{T("about_p2")}</p>
      <p>{T("about_p3")}</p>
      <p>{T("about_p4")}</p>
      <p><a class="btn btn-gold" href="inscriere.html">{T("about_btn_enroll")}</a> <a class="btn btn-ghost" href="program.html">{T("about_btn_program")}</a></p></section>
    <aside class="panel"><div class="coord" style="flex-direction:column;align-items:center;text-align:center">
      <div class="ph ph-a" style="width:200px"><img src="{P}assets/a-portrait.jpg" alt="Dan D. Farcaș" width="246" height="288"></div>
      <div class="ph art-b-ph" style="width:200px"><img src="{P}assets/b-portrait.jpg" alt="Dan D. Farcaș" width="244" height="252"></div>
      <div class="who"><b>Dan D. Farcaș</b><span>{T("coord_role1")}</span><span>{T("coord_role2")}</span></div></div>
      <p class="note" style="text-align:center;margin-top:14px"><a href="{ASFAN}" rel="noopener">www.asfanufo.ro</a><br>{E(" · ".join(UI["motto"].split("<br>")))}</p></aside>
  </div>
  <section class="sec" aria-labelledby="h-af">
    <h2 id="h-af">{T("posters_h")} <span class="sub">{T("posters_sub")}</span></h2>
    <div class="posters">
      <button type="button" data-poster="assets/afis-moai.jpg"><img src="{P}assets/afis-moai.jpg" alt="{A("poster_moai_alt")}" width="1024" height="1536" loading="lazy"><span>{T("poster_moai")}</span></button>
      <button type="button" data-poster="assets/afis-anzi.jpg"><img src="{P}assets/afis-anzi.jpg" alt="{A("poster_anzi_alt")}" width="1024" height="1536" loading="lazy"><span>{T("poster_anzi")}</span></button>
    </div>
    <p class="note">{T("posters_note")}</p>
  </section>

  <section class="sec"><h2>{T("brief_h")}</h2>
    <div class="facts">
      <div class="fact"><small>{T("f_period")}</small><b>{T("f_period_v")}</b></div>
      <div class="fact"><small>{T("f_day")}</small><b>{T("f_day_v")}</b></div>
      <div class="fact"><small>{T("fact_format")}</small><b>{T("f_format_v")}</b></div>
      <div class="fact"><small>{T("f_lang")}</small><b>{T("f_lang_v")}</b></div>
      <div class="fact"><small>{T("f_cost")}</small><b>{T("f_cost_v")}</b></div>
      <div class="fact"><small>{T("f_diploma")}</small><b>{T("f_diploma_v")}</b></div>
      <div class="fact"><small>{T("f_seats")}</small><b>{T("f_seats_v")}</b></div>
      <div class="fact"><small>{T("f_deadline")}</small><b>{T("f_deadline_v")}</b></div>
      <div class="fact"><small>{T("f_sessions")}</small><b>14</b></div>
    </div></section>
  <section class="sec"><h2>{T("faq_h")}</h2>
'''
    for q, a in LD["faq"] + [[UI["faq_lang_q"], UI["faq_lang_a"]]]:
        b += f'    <details class="ac"><summary><span class="tt">{E(q)}</span></summary><div class="body" style="padding-left:16px"><p>{E(rep(a))}</p></div></details>\n'
    b += '''  </section>
</div>
'''
    return h + b + foot()

# ------------------------------------------------------------------ inscriere
def page_inscriere():
    h = head(T("title_enroll"), T("desc_enroll"), "inscriere", "inscriere.html")
    conds = "".join(f"<li>{E(x)}</li>" for x in UI["enr_cond"].split("|"))
    b = notice() + f'''<div class="wrap">
  <div class="page-head">{crumbs(T("nav_enroll"))}
    <h1>{T("enr_h1")}</h1>
    <p class="lead">{T("enr_lead")}</p></div>
  <div class="count"><span class="lbl">{T("enr_cd_label")}</span><div class="cd" data-countdown="2026-11-17T23:59:59+02:00" data-done="{A("enr_cd_done")}"></div></div>
  <div class="grid2" style="margin-top:20px">
    <section class="panel"><h2 style="margin-top:0">{T("enr_form_h")}</h2>
      <p class="note">{T("enr_note1")}</p>
      <form class="enr" novalidate data-ro-subject="Înscriere curs „Introducere în ufologie” (seria a patra)">
        <button type="submit" class="vh" tabindex="-1" aria-hidden="true">{A("enr_send")}</button>
        <label for="nume-{CODE}">{T("enr_name")}</label><input id="nume-{CODE}" name="nume" type="text" required autocomplete="name">
        <label for="email-{CODE}">{T("enr_email")}</label><input id="email-{CODE}" name="email" type="email" required autocomplete="email" inputmode="email">
        <label for="loc-{CODE}">{T("enr_loc")}</label><input id="loc-{CODE}" name="loc" type="text" autocomplete="address-level2">
        <label for="motiv-{CODE}">{T("enr_motiv")}</label><textarea id="motiv-{CODE}" name="motiv"></textarea>
        <p style="margin-top:16px"><a class="btn btn-gold enr-send" href="mailto:{MAIL}">{T("enr_send")}</a> <button class="btn btn-ghost enr-copy" type="button" data-copied="{JS("copied")}" data-fail="{JS("copy_fail")}">{T("enr_copy")}</button></p>
        <p class="note">{T("enr_note2")}</p>
        <p class="ok enr-ok" hidden>{T("enr_ok")}</p>
      </form></section>
    <aside class="panel"><h2 style="margin-top:0">{T("enr_direct_h")}</h2>
      <p>{T("enr_write")} <a href="mailto:{MAIL}"><b>{MAIL}</b></a></p>
      <p><button class="btn btn-ghost" type="button" data-copy="{MAIL}" data-copied="{JS("copied")}">{T("enr_copy_addr")}</button></p>
      <hr style="border:0;border-top:1px solid var(--line)"><h3>{T("enr_cond_h")}</h3>
      <ul>{conds}</ul></aside>
  </div>
</div>
'''
    return h + b + foot()

# ------------------------------------------------------------------ qr page
def page_qr():
    h = head(T("title_qr"), T("desc_qr"), "qr", "qr.html")
    b = notice() + f'''<div class="wrap">
  <div class="page-head">{crumbs(T("nav_qr"))}
    <h1>{T("qr_h1")}</h1>
    <p class="lead">{T("qr_lead")}</p>
    <p class="toolbar"><button class="btn btn-gold" type="button" onclick="print()">{T("qr_print")}</button></p></div>
  {qr_block()}
  <p class="note" style="margin-top:14px">{T("qr_note")}</p>
</div>
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
              "lb_aria","lb_dl","lb_close","lb_alt","foot_hand","foot_hand2","foot_tag_b","foot_tag_s","foot_qr_aria","foot_qr_alt","share_h","share_native","share_copy","share_via","share_text","lang_notice")}
    open(f"{OUT}/assets/i18n-{CODE}.js","w",encoding="utf-8").write("window.ASFAN_I18N="+json.dumps(dict(lang=CODE,js=LD["js"],labels=[s["label"] for s in SESS],chrome=chrome,
        titles={"index":UI["title_index"],"program":UI["title_program"],"detalii":UI["title_about"],"inscriere":UI["title_enroll"],"qr":UI["title_qr"]},
        cd_start=UI["cd_start"]),ensure_ascii=False)+";\n")
    write("index.html", page_index()); write("program.html", page_program()); write("detalii.html", page_detalii())
    write("inscriere.html", page_inscriere()); write("qr.html", page_qr())
    for s in SESS: write(f"sesiune-{s['n']}.html", page_session(s))

open(f"{OUT}/assets/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#06142f"/><ellipse cx="32" cy="30" rx="24" ry="8" fill="#4cc9ff"/><ellipse cx="32" cy="26" rx="11" ry="9" fill="#bfe6ff"/><path d="M22 38l-6 14h32l-6-14z" fill="#f7b733" opacity=".55"/></svg>')
open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
pages = ["index.html", "program.html", "detalii.html", "inscriere.html", "qr.html"] + [f"sesiune-{i}.html" for i in range(1, 15)]
def alt(p): return "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{loc_url(l, p)}"/>' for l in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{loc_url("ro", p)}"/>'
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "".join(f"<url><loc>{loc_url(l, p)}</loc>{alt(p)}</url>\n" for p in pages for l in LANGS) + "</urlset>\n")
print("OK", len(LANGS), "limbi;", len(pages) * len(LANGS), "pagini")
