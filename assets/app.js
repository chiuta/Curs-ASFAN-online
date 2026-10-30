(function(){
'use strict';
var root=document.documentElement;
/* ---- Theme ---- */
function setTheme(t,save){root.setAttribute('data-theme',t);if(save){try{localStorage.setItem('asfan-theme-v3',t)}catch(e){}}
  document.querySelectorAll('.theme-switch button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.theme===t)});
  var m=document.querySelector('meta[name=theme-color]');if(m)m.content=t==='anzi'?'#0b1b3b':'#030a1c';}
var q=new URLSearchParams(location.search).get('tema'),saved=null;try{saved=localStorage.getItem('asfan-theme-v3')}catch(e){}
setTheme(q==='anzi'||q==='moai'?q:(saved==='anzi'||saved==='moai'?saved:'moai'));
document.querySelectorAll('.theme-switch button').forEach(function(b){b.addEventListener('click',function(){setTheme(b.dataset.theme,true)})});
/* ---- Menu ---- */
var bm=document.querySelector('.btn-menu'),nav=document.querySelector('nav.main');
if(bm){bm.addEventListener('click',function(e){e.stopPropagation();var o=nav.classList.toggle('open');bm.setAttribute('aria-expanded',o)});
  function closeNav(){nav.classList.remove('open');bm.setAttribute('aria-expanded','false')}
  nav.addEventListener('click',function(e){if(e.target.closest('a'))closeNav()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){closeNav();bm.focus()}});
  document.addEventListener('click',function(e){if(nav.classList.contains('open')&&!nav.contains(e.target))closeNav()})}
/* ---- Stars ---- */
(function(){var c=document.getElementById('stars');if(!c)return;var x=c.getContext('2d'),w,h,st=[],rm=matchMedia('(prefers-reduced-motion:reduce)').matches,last=0,raf=0;
  function render(t){x.clearRect(0,0,w,h);for(var i=0;i<st.length;i++){var s=st[i];x.globalAlpha=.35+.65*Math.abs(Math.sin(s.p+t*s.s));x.fillStyle=i%9===0?'#9fd8ff':'#fff';x.fillRect(s.x,s.y,s.r,s.r)}x.globalAlpha=1}
  function rs(){var d=Math.min(devicePixelRatio||1,2);w=c.width=innerWidth*d;h=c.height=innerHeight*d;st=[];var n=Math.min(140,Math.round(innerWidth*innerHeight/11000));
    for(var i=0;i<n;i++)st.push({x:Math.random()*w,y:Math.random()*h,r:(Math.random()*1.3+.6)*d,p:Math.random()*6.28,s:Math.random()*.02+.004});render(0)}
  function loop(n){raf=requestAnimationFrame(loop);if(n-last<50)return;last=n;render(n/16)}
  function run(){if(rm||raf)return;raf=requestAnimationFrame(loop)}
  function stop(){if(raf){cancelAnimationFrame(raf);raf=0}}
  document.addEventListener('visibilitychange',function(){document.hidden?stop():run()});
  rs();run();addEventListener('resize',function(){clearTimeout(rs.t);rs.t=setTimeout(rs,200)})})();
/* ---- Sessions / countdown ---- */
function I(){return window.ASFAN_I18N||{js:{},labels:[],cd_start:''}}
function fmt(t,o){return String(t).replace(/\{(\w+)\}/g,function(m,k){return o[k]!==undefined?o[k]:m})}
var S=window.ASFAN_SESSIONS||[];
function nextIdxNow(){var n=Date.now();for(var i=0;i<S.length;i++){if(new Date(S[i].end).getTime()>n)return i}return -1}
document.querySelectorAll('[data-sess]').forEach(function(el){var n=+el.dataset.sess,s=S[n-1];if(!s)return;
  if(new Date(s.end).getTime()<Date.now())el.classList.add('past');else if(n-1===nextIdxNow())el.classList.add('next')});
var cds=[].slice.call(document.querySelectorAll('[data-countdown]'));
function paint(el){var d=new Date(el.dataset.countdown).getTime()-Date.now(),j=I().js;
  if(d<=0){el.innerHTML='<span class="ok">'+(el.dataset.done||j.started||'')+'</span>';return}
  var D=Math.floor(d/864e5),H=Math.floor(d%864e5/36e5),M=Math.floor(d%36e5/6e4),Sx=Math.floor(d%6e4/1e3);
  el.innerHTML='<div><b>'+D+'</b><small>'+j.u_d+'</small></div><div><b>'+H+'</b><small>'+j.u_h+'</small></div><div><b>'+M+'</b><small>'+j.u_m+'</small></div><div><b>'+Sx+'</b><small>'+j.u_s+'</small></div>'}
function nextBar(){var ni=nextIdxNow(),i18=I();
  document.querySelectorAll('[data-next-wrap]').forEach(function(w){if(w.offsetParent===null&&w.style.display!=='none')return;
    var lab=w.querySelector('[data-next-label]'),cd=w.querySelector('[data-next-cd]');if(!lab)return;
    if(ni<0){lab.textContent=i18.js.course_over||'';if(cd)cd.style.display='none';return}
    var lb=(i18.labels||[])[ni]||'';
    lab.textContent=ni===0?fmt(i18.js.course_starts,{label:lb}):fmt(i18.js.next_session,{n:ni+1,label:lb});
    if(cd){cd.style.display='';cd.dataset.countdown=S[ni].start}})}
function tick(){nextBar();cds.forEach(function(el){if(el.offsetParent!==null)paint(el)})}
window.__asfanTick=tick;tick();setInterval(function(){if(!document.hidden)tick()},1000);
/* ---- Copy ---- */
document.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){var t=b.dataset.copy,o=b.textContent,ok=b.dataset.copied||'OK';
  (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent=ok},function(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');b.textContent=ok}catch(e){b.textContent=t}a.remove()});
  setTimeout(function(){b.textContent=o},2000)})});
/* ---- Reveal ---- */
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.08});document.querySelectorAll('.reveal').forEach(function(e){io.observe(e)})}else document.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in')});
/* ---- Lightbox ---- */
var lb=document.getElementById('lb');
document.querySelectorAll('[data-poster]').forEach(function(b){b.addEventListener('click',function(){if(!lb||!lb.showModal){window.open(b.dataset.poster,'_blank');return}
  lb.querySelector('img').src=b.dataset.poster;lb.querySelector('a.dl').href=b.dataset.poster;lb.showModal()})});
if(lb){lb.addEventListener('click',function(e){if(e.target===lb||e.target.classList.contains('in'))lb.close()});var cl=lb.querySelector('.close');if(cl)cl.addEventListener('click',function(){lb.close()})}
/* ---- Program accordion ---- */
function openHash(){if(location.hash&&location.hash.indexOf('#/')!==0){var el=null;try{el=document.querySelector(location.hash)}catch(e){}if(el&&el.tagName==='DETAILS'){el.open=true;setTimeout(function(){el.scrollIntoView({behavior:'smooth',block:'start'})},60)}}}
openHash();addEventListener('hashchange',openHash);
document.querySelectorAll('.expand-all').forEach(function(ea){var scope=ea.closest('.wrap'),st=!!scope.querySelector('details.ac[open]');
  ea.addEventListener('click',function(){st=!st;scope.querySelectorAll('details.ac').forEach(function(d){d.open=st});ea.textContent=st?ea.dataset.collapse:ea.dataset.expand})});
document.querySelectorAll('.sess-filter').forEach(function(sf){var scope=sf.closest('.wrap');
  function fold(t){t=String(t).toLowerCase();try{t=t.normalize('NFD').replace(/[\u0300-\u036f]/g,'')}catch(e){}return t.replace(/\s+/g,' ').trim()}
  var nr=scope.querySelector('.no-res');
  sf.addEventListener('input',function(){var v=fold(sf.value),n=0;scope.querySelectorAll('details.ac').forEach(function(d){var m=!v||fold(d.textContent).indexOf(v)>-1;d.style.display=m?'':'none';if(m)n++;if(v&&m)d.open=true});if(nr)nr.hidden=n>0||!v})});
/* ---- Language menu ---- */
document.querySelectorAll('details.lang').forEach(function(d){
  document.addEventListener('click',function(e){if(d.open&&!d.contains(e.target))d.open=false});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&d.open){d.open=false;var s=d.querySelector('summary');if(s)s.focus()}});
  d.querySelectorAll('a[data-lang-link]').forEach(function(a){a.addEventListener('click',function(){try{localStorage.setItem('asfan-lang',a.dataset.langLink)}catch(e){}})})});
/* ---- Enrollment form -> mailto (e-mailul este redactat în română, pentru organizatori) ---- */
var TO='adrian.urzica@gmail.com';
document.querySelectorAll('form.enr').forEach(function(f){
  var snd=f.querySelector('.enr-send'),cp=f.querySelector('.enr-copy'),okm=f.querySelector('.enr-ok'),SUBJ=f.dataset.roSubject||'Înscriere curs';
  function build(){var n=f.nume.value.trim(),e=f.email.value.trim(),l=f.loc.value.trim(),m=f.motiv.value.trim();
    var sub=SUBJ+(n?' – '+n:'');
    var body='Bună ziua,\n\nDoresc să mă înscriu la cursul „Introducere în ufologie” (seria a patra), organizat de ASFAN, 18 noiembrie 2026 – 26 mai 2027, prin ZOOM.\n\nNume și prenume: '+n+'\nAdresa de e-mail pentru link-urile ZOOM: '+e+(l?'\nLocalitatea: '+l:'')+(m?'\nCâteva cuvinte despre interesul meu: '+m:'')+'\n\nÎnțeleg că participarea este gratuită, că locurile sunt limitate și că diploma se poate solicita cu cel mult trei absențe.\n\nMulțumesc!\n'+n;
    return {sub:sub,body:body}}
  function mailto(){var b=build();return 'mailto:'+TO+'?subject='+encodeURIComponent(b.sub)+'&body='+encodeURIComponent(b.body.replace(/\n/g,'\r\n'))}
  function refresh(){if(snd)snd.setAttribute('href',mailto())}
  f.addEventListener('input',refresh);refresh();
  if(snd)snd.addEventListener('click',function(ev){if(!f.checkValidity()){ev.preventDefault();f.reportValidity();return}refresh();if(okm)okm.hidden=false});
  f.addEventListener('submit',function(ev){ev.preventDefault();if(snd)snd.click()});
  if(cp)cp.addEventListener('click',function(){if(!f.checkValidity()){f.reportValidity();return}var b=build(),j=I().js,o=cp.dataset.orig||(cp.dataset.orig=cp.textContent),t=(j.copy_to||'To')+': '+TO+'\n'+(j.copy_subject||'Subject')+': '+b.sub+'\n\n'+b.body;
    (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){cp.textContent=cp.dataset.copied},function(){cp.textContent=cp.dataset.fail});setTimeout(function(){cp.textContent=o},2200)})});
/* ---- Share ---- */
document.querySelectorAll('.share-native').forEach(function(b){if(!navigator.share)return;b.hidden=false;
  b.addEventListener('click',function(){var w=b.closest('[data-share]');navigator.share({title:w.dataset.shareTitle,text:w.dataset.shareText,url:w.dataset.shareUrl}).catch(function(){})})});
})();

/* ---- Termen înscriere: după 17 nov. 2026 ascunde butoanele de înscriere din bară/antet ---- */
(function(){var dl=new Date('2026-11-17T23:59:59+02:00').getTime();function chk(){if(Date.now()>dl)document.documentElement.classList.add('enr-closed')}chk();setInterval(chk,30000)})();
/* ---- Sugestie de limbă (doar pe pagina română, fără redirecționare automată) ---- */
(function(){if(window.__SINGLE__||document.documentElement.lang!=='ro')return;
  var M={en:'Read this page in English',fr:'Lire cette page en français',it:'Leggi questa pagina in italiano',es:'Leer esta página en español',pt:'Ler esta página em português',de:'Diese Seite auf Deutsch lesen',hu:'Olvassa el magyarul'};
  try{if(sessionStorage.getItem('asfan-sug')||localStorage.getItem('asfan-lang')==='ro')return}catch(e){}
  var nl=navigator.languages||[navigator.language||'ro'],c=null;for(var i=0;i<nl.length;i++){var x=String(nl[i]).slice(0,2).toLowerCase();if(x==='ro')return;if(M[x]){c=x;break}}
  if(!c)return;var h=document.querySelector('header.topbar');if(!h)return;
  var d=document.createElement('aside');d.className='lang-sug';d.setAttribute('aria-label','Language');d.innerHTML='<div class="wrap"><a hreflang="'+c+'" lang="'+c+'" href="'+c+'/">'+M[c]+' →</a><button type="button" aria-label="OK">×</button></div>';
  d.querySelector('button').addEventListener('click',function(){d.remove();try{sessionStorage.setItem('asfan-sug','1')}catch(e){}});
  h.parentNode.insertBefore(d,h.nextSibling)})();
