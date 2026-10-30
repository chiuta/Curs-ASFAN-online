#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Combină site-ul multilingv (generat de build.py) într-un singur fișier HTML, cu imagini încorporate și comutator de limbă."""
import re, os, io, json, base64, glob, posixpath, html as _h
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE_DIR") or os.path.dirname(ROOT)
A = SITE + "/assets/"
rd = lambda p: open(p, encoding="utf-8").read()
LANGS = ["ro", "en", "fr", "it", "es", "pt", "de", "hu"]
PAGES = ["index"]

def jpeg_uri(path, maxw=None, q=82):
    if not os.path.exists(path): path = os.path.join(ROOT, "art", os.path.basename(path))   # imagini doar pentru varianta cu afiș
    im = Image.open(path).convert("RGB")
    if maxw and im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
def raw_uri(path, mime): return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

IMG = {}
for k in ["a-bottom","a-moai","a-portrait","a-ufo","b-earth","b-machu","b-portrait","b-ufo"] + [f"{p}-t{i}" for p in "ab" for i in range(1,15)]:
    IMG[k + ".jpg"] = jpeg_uri(A + k + ".jpg", q=84)
IMG["afis-moai.jpg"] = jpeg_uri(A + "afis-moai.jpg", maxw=900, q=78)
IMG["afis-anzi.jpg"] = jpeg_uri(A + "afis-anzi.jpg", maxw=900, q=78)
for n in ("qr-curs", "qr-asfan"):
    IMG[n + ".png"] = raw_uri(A + n + ".png", "image/png"); IMG[n + ".svg"] = raw_uri(A + n + ".svg", "image/svg+xml")
IMG["logo.png"] = raw_uri(A + "logo.png", "image/png"); IMG["favicon.svg"] = raw_uri(A + "favicon.svg", "image/svg+xml")

def page_path(lang, page): return f"{SITE}/{page}.html" if lang == "ro" else f"{SITE}/{lang}/{page}.html"

def resolve(lang, href):
    """href relativ (…​.html) dintr-o pagină din `lang` -> (limbă țintă, pagină)"""
    base = "" if lang == "ro" else lang
    p = posixpath.normpath(posixpath.join(base, href)) if base else posixpath.normpath(href)
    parts = p.split("/")
    tl = parts[0] if parts[0] in LANGS else "ro"
    page = parts[-1][:-5]
    return tl, page
def hh(tl, page): return "#/" + ("" if tl == "ro" else tl + "/") + ("" if page == "index" else page)

def fix_links(s, lang):
    s = re.sub(r'href="((?:\.\./)?(?:[a-z]{2}/)?[\w-]+\.html)(#[^"]*)?"', lambda m: 'href="%s"' % hh(*resolve(lang, m.group(1))), s)
    s = re.sub(r'href="[^"]*calendar/[^"]*" data-ics="([^"]+)" download', lambda m: f'href="#" data-ics="{lang}/{m.group(1)}"', s)
    s = re.sub(r'href="(?:\.\./)?assets/([\w-]+\.(?:png|svg))" download="([^"]+)"', r'href="#" data-dl="\1" download="\2"', s)
    s = re.sub(r'src="(?:\.\./)?assets/([\w-]+\.(?:jpg|svg|png))"', r'data-img="\1"', s)
    s = re.sub(r'data-poster="assets/([\w-]+\.jpg)"', r'data-poster="\1"', s)
    s = s.replace('rel="noopener"', 'target="_blank" rel="noopener noreferrer"')
    s = re.sub(r' aria-current="page"', '', s)
    return s

sections, titles = "", {}
for lang in LANGS:
    for pg in PAGES:
        h = rd(page_path(lang, pg))
        title = _h.escape(_h.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1)), quote=True)
        b = re.search(r'<main id="main">\n(.*?)</main>', h, re.S).group(1)
        b = fix_links(b, lang)
        # id-uri unice între limbi
        b = re.sub(r'id="(s\d+|h-st|h-inv|h-plan|h-enr|h-qr|top|inv|plan|inscriere|qr)"', rf'id="{lang}-\1"', b)
        b = re.sub(r'aria-labelledby="(h-st|h-inv|h-plan|h-enr|h-qr)"', rf'aria-labelledby="{lang}-\1"', b)
        b = re.sub(r'href="#(top|inv|plan|inscriere|qr)"', r'href="#\1"', b)
        sections += f'<section class="page" data-page="{lang}/{pg}" data-title="{title}"{"" if (lang, pg) == ("ro", "index") else " hidden"}>\n{b}</section>\n'

idx = rd(f"{SITE}/index.html")
head = idx.split('<main id="main">')[0]
tail = idx.split("</main>", 1)[1]
head = re.sub(r'<link rel="alternate"[^>]*>\n?', '', head)
head = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>\n?', '', head)
head = re.sub(r'<meta property="og:(site_name|locale:alternate|image:[a-z]+)"[^>]*>', '', head)
head = re.sub(r'<link rel="canonical"[^>]*>\n?', '', head)
head = re.sub(r'<meta property="og:(url|image)"[^>]*>', '', head)
head = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', head, flags=re.S)
head = head.replace('<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">', '<link rel="icon" href="" id="fav">')
head = head.replace('<link rel="stylesheet" href="assets/style.css">\n', '')
head = fix_links(head, "ro"); tail = fix_links(tail, "ro")
head = head.replace('<a class="skip" href="#main"', '<a class="skip" href="#/" data-skip')
tail = re.sub(r'<script src="assets/[^"]+"></script>\n?', '', tail)
head = re.sub(r'<body data-page="[^"]*">', '<body data-page="index">', head)

css = rd(A + "style.css")
css = css.replace('html[data-theme="moai"] .foot-art{background-image:url(a-bottom.jpg)}', 'html[data-theme="moai"] .foot-art{background-image:var(--foot-a)}')
css = css.replace('html[data-theme="anzi"] .foot-art{background-image:url(b-earth.jpg)}', 'html[data-theme="anzi"] .foot-art{background-image:var(--foot-b)}')
for fn in ("mont-latin", "mont-ext", "ss-latin", "ss-ext"):
    css = css.replace(f"url(fonts/{fn}.woff2)", "url(" + raw_uri(A + f"fonts/{fn}.woff2", "font/woff2") + ")")
css += "\n[hidden]{display:none!important}\nsection.page{display:block}\n"

ics = {}
for lang in LANGS:
    d = f"{SITE}/calendar" + ("" if lang == "ro" else f"/{lang}")
    for p in glob.glob(d + "/*.ics"): ics[f"{lang}/{os.path.basename(p)[:-4]}"] = open(p, encoding="utf-8", newline="").read()

ALL = {}
for lang in LANGS:
    t = rd(A + f"i18n-{lang}.js"); ALL[lang] = json.loads(t[t.index("=") + 1:].strip().rstrip(";"))

app = rd(A + "app.js")
sessions_js = rd(A + "sessions.js")

glue = r'''
(function(){
var IMG=window.__IMG__,ALL=window.__I18N__,LANGS=Object.keys(ALL),root=document.documentElement;
window.__SINGLE__=true;
document.querySelectorAll('img[data-img]').forEach(function(i){i.src=IMG[i.dataset.img]});
var fav=document.getElementById('fav');if(fav)fav.href=IMG['favicon.svg'];
root.style.setProperty('--foot-a','url('+IMG['a-bottom.jpg']+')');root.style.setProperty('--foot-b','url('+IMG['b-earth.jpg']+')');
document.querySelectorAll('a[data-dl]').forEach(function(a){a.href=IMG[a.dataset.dl]});
document.querySelectorAll('[data-poster]').forEach(function(b){b.dataset.poster=IMG[b.dataset.poster]});
document.querySelectorAll('a[data-ics]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();
  var t=window.__ICS__[a.dataset.ics];if(!t)return;var u=URL.createObjectURL(new Blob([t],{type:'text/calendar;charset=utf-8'})),d=document.createElement('a');
  d.href=u;d.download=a.dataset.ics.replace('/','-')+'.ics';d.target='_blank';document.body.appendChild(d);try{d.click()}catch(x){window.open('data:text/calendar;charset=utf-8,'+encodeURIComponent(t))}d.remove();setTimeout(function(){URL.revokeObjectURL(u)},4000)})});
var sk=document.querySelector('[data-skip]');if(sk)sk.addEventListener('click',function(e){e.preventDefault();var m=document.getElementById('main');m.setAttribute('tabindex','-1');m.focus()});
var pages=document.querySelectorAll('section.page'),nav=document.querySelector('nav.main'),bm=document.querySelector('.btn-menu');
function parse(h){h=(typeof h==='string'?h:location.hash).replace(/^#\/?/,'').split('?')[0];var p=h.split('/'),l='ro';if(LANGS.indexOf(p[0])>-1&&p[0]!=='ro')l=p.shift();else if(p[0]==='ro')p.shift();
  var pg=p.join('/')||'index';if(pg==='index.html')pg='index';return{lang:l,page:pg}}
function hash(l,pg){return '#/'+(l==='ro'?'':l+'/')+(pg==='index'?'':pg)}
function detect(){var s=null;try{s=localStorage.getItem('asfan-lang')}catch(e){}if(s&&ALL[s])return s;
  var nl=(navigator.languages||[navigator.language||'ro']);for(var i=0;i<nl.length;i++){var c=String(nl[i]).slice(0,2).toLowerCase();if(ALL[c])return c}return 'ro'}
function applyChrome(l){var C=ALL[l].chrome;
  document.querySelectorAll('[data-k]').forEach(function(e){if(C[e.dataset.k]!==undefined)e.innerHTML=C[e.dataset.k]});
  document.querySelectorAll('[data-k-aria]').forEach(function(e){if(C[e.dataset.kAria]!==undefined)e.setAttribute('aria-label',C[e.dataset.kAria].replace(/<[^>]+>/g,''))});
  document.querySelectorAll('[data-k-alt]').forEach(function(e){if(C[e.dataset.kAlt]!==undefined)e.setAttribute('alt',C[e.dataset.kAlt])})}
function route(hs){var r=parse(hs),first=!window.__routed;
  if(first&&(typeof hs!=='string')&&!location.hash){var d=detect();if(d!=='ro'){r={lang:d,page:'index'};try{history.replaceState(null,'',hash(d,'index'))}catch(e){}}}
  var key=r.lang+'/'+r.page,found=null;
  pages.forEach(function(p){if(p.dataset.page===key)found=p});
  if(!found){found=document.querySelector('[data-page="'+r.lang+'/index"]');r.page='index';key=r.lang+'/index'}
  pages.forEach(function(p){p.hidden=p!==found});
  root.lang=r.lang;window.ASFAN_I18N=ALL[r.lang];applyChrome(r.lang);
  (function(){var C=ALL[r.lang].chrome,SITEU='https://curs.asfan.online/'+(r.lang==='ro'?'':r.lang+'/'),url=SITEU+(r.page==='index'?'':r.page+'.html'),txt=C.share_text,ttl=ALL[r.lang].titles.index,E=encodeURIComponent;
    document.querySelectorAll('[data-share]').forEach(function(w){w.dataset.shareUrl=url;w.dataset.shareTitle=ttl;w.dataset.shareText=txt;
      var H={Facebook:'https://www.facebook.com/sharer/sharer.php?u='+E(url),X:'https://twitter.com/intent/tweet?url='+E(url)+'&text='+E(txt),LinkedIn:'https://www.linkedin.com/sharing/share-offsite/?url='+E(url),
        WhatsApp:'https://wa.me/?text='+E(txt+' '+url),Telegram:'https://t.me/share/url?url='+E(url)+'&text='+E(txt),'E-mail':'mailto:?subject='+E(ttl)+'&body='+E(txt+'\n\n'+url)};
      w.querySelectorAll('a[data-net]').forEach(function(a){a.href=H[a.dataset.net];a.setAttribute('aria-label',C.share_via.replace('{net}',a.dataset.net))});
      var cb=w.querySelector('button[data-copy]');if(cb)cb.dataset.copy=url})})();
  document.body.dataset.page=r.page.indexOf('sesiune-')===0?'sesiune':r.page;
  document.title=found.dataset.title;var sr=document.getElementById('sr');if(sr)sr.textContent=found.dataset.title;
  var top=r.page.indexOf('sesiune-')===0?'program':r.page;
  document.querySelectorAll('[data-nav]').forEach(function(a){var t=a.dataset.nav||'index';a.setAttribute('href',hash(r.lang,t));
    if(a.classList.contains('lnk')){if(t===top)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')}});
  document.querySelectorAll('a[data-lang-link]').forEach(function(a){var l=a.dataset.langLink;a.setAttribute('href',hash(l,r.page));if(l===r.lang)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')});
  document.querySelectorAll('details.lang').forEach(function(d){d.open=false;var b=d.querySelector('summary b'),sm=d.querySelector('summary');if(b)b.textContent=r.lang.toUpperCase();if(sm)sm.setAttribute('aria-label',r.lang.toUpperCase()+' – '+ALL[r.lang].chrome.lang_aria)});
  if(nav){nav.classList.remove('open');if(bm)bm.setAttribute('aria-expanded','false')}
  window.scrollTo(0,0);if(window.__asfanTick)window.__asfanTick();
  var mm=document.getElementById('main');if(mm&&window.__routed){mm.setAttribute('tabindex','-1');try{mm.focus({preventScroll:true})}catch(e){}}window.__routed=true}
addEventListener('hashchange',function(){route()});addEventListener('popstate',function(){route()});
document.addEventListener('click',function(e){var sc=e.target.closest?e.target.closest('a[data-sec]'):null;
  if(sc&&!e.defaultPrevented&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey){e.preventDefault();var id=sc.dataset.sec,t=id==='top'?null:document.getElementById(root.lang+'-'+id);
    if(t){var y=t.getBoundingClientRect().top+window.pageYOffset-64;window.scrollTo({top:y,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});try{t.setAttribute('tabindex','-1');t.focus({preventScroll:true})}catch(x){}}
    else window.scrollTo({top:0,behavior:'smooth'});
    if(nav){nav.classList.remove('open');if(bm)bm.setAttribute('aria-expanded','false')}return}
  var a=e.target.closest?e.target.closest('a[href^="#/"]'):null;if(!a||e.defaultPrevented||e.ctrlKey||e.metaKey||e.shiftKey)return;
  e.preventDefault();var h=a.getAttribute('href');if(a.dataset.langLink){try{localStorage.setItem('asfan-lang',a.dataset.langLink)}catch(x){}}
  try{history.pushState(null,'',h)}catch(x){try{location.hash=h}catch(y){}}route(h)});
route();
})();
'''

out = head
out = out.replace('<canvas id="stars" aria-hidden="true"></canvas>', '<canvas id="stars" aria-hidden="true"></canvas>\n<div id="sr" class="vh" role="status" aria-live="polite"></div>\n<noscript><p style="margin:0;padding:14px;background:#7a1d1d;color:#fff;position:relative;z-index:9">This site needs JavaScript · Acest site are nevoie de JavaScript.</p></noscript>')
out = out.replace("</head>", "<style>\n" + css + "\n</style>\n</head>")
out += '<main id="main">\n' + sections + '</main>\n' + tail
out = out.replace("</body></html>", "")
_used = set(re.findall(r'data-img="([^"]+)"', sections + head + tail)) | {"a-bottom.jpg", "b-earth.jpg", "favicon.svg", "logo.png", "qr-curs.png", "qr-curs.svg", "qr-asfan.png", "qr-asfan.svg"} | {m for m in re.findall(r'data-dl="([^"]+)"', sections)} | set(re.findall(r'data-poster="([^"]+)"', sections))
IMG = {k: v for k, v in IMG.items() if k in _used}
out += "<script>window.__IMG__=" + json.dumps(IMG) + ";window.__I18N__=" + json.dumps(ALL, ensure_ascii=False) + ";window.__ICS__=" + json.dumps(ics, ensure_ascii=False) + ";</script>\n"
out += "<script>\n" + sessions_js + "\n" + app + "\n" + glue + "\n</script>\n</body></html>\n"
dst = os.environ.get("DST") or os.path.join(os.path.dirname(ROOT), "dist", "curs-asfan-online.html")
os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, "w", encoding="utf-8").write(out)
print("OK", dst, round(len(out.encode()) / 1024), "KB")
