#!/usr/bin/env python3
"""Usage: python3 check.py xx  -> validates xx.json against ro.json"""
import json,re,sys
code=sys.argv[1]
ro=json.load(open('/home/claude/i18n/ro.json',encoding='utf-8'));t=json.load(open(f'/home/claude/i18n/{code}.json',encoding='utf-8'))
bad=[]
tag=lambda s:sorted(re.findall(r'</?[a-zA-Z]+[^>]*>',s))
ph=lambda s:sorted(re.findall(r'\{[A-Za-z_0-9]+\}',s))
def walk(a,b,path):
    if isinstance(a,dict):
        if set(a)!=set(b): bad.append((path,'keys differ',sorted(set(a)^set(b))));return
        for k in a: walk(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        if len(a)!=len(b): bad.append((path,'len',len(a),len(b)));return
        for i,(x,y) in enumerate(zip(a,b)): walk(x,y,f'{path}[{i}]')
    else:
        if not isinstance(b,str) or (not b.strip() and not re.search(r'(months|mon3)\[0\]',path)): bad.append((path,'empty/nonstr'));return
        if path.startswith('/meta'): return
        if path.startswith('/dates') and not any(x in path for x in('fmt_',)): return
        if ph(a)!=ph(b): bad.append((path,'placeholders',ph(a),ph(b)))
        if '/dates/' not in path:
            if tag(a)!=tag(b): bad.append((path,'tags',tag(a),tag(b)))
            if a.count('|')!=b.count('|'): bad.append((path,'pipes'))
            if a.count('\n')!=b.count('\n'): bad.append((path,'newlines'))
walk(ro,t,'')
if len(t['dates']['months'])!=13 or len(t['dates']['mon3'])!=13 or len(t['dates']['wd'])!=7: bad.append(('dates','array lengths'))
print('OK' if not bad else '\n'.join(map(str,bad)))
