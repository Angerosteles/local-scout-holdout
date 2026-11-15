"""Print the summary tables from holdout_pomiar.py output.

Usage: python holdout_tabela.py results.json SETTING   (default, deep, other_on, deep_other_on; v175 for 1.7.5)"""
import json,sys,collections
d=json.load(open(sys.argv[1])); setting=sys.argv[2]; D=d[setting]
CATS=['email','card','iban','pesel','ssn','secret','phone','address','name']
def agg(filter_key):
    c=collections.Counter()
    for key,v in D.items():
        k,l=key.split('|')
        if filter_key(k,l):
            c.update(v)
    return c
print(f'== {setting}')
print(f"{'category':8} {'fully':>11} {'partly':>11} {'false traps':>17} {'visible fp/100':>16}")
for k in CATS:
    for lang in ('ALL','EN','PL'):
        c=agg(lambda kk,ll: kk==k and (lang=='ALL' or ll==lang))
        n=c[k]
        if not n: continue
        print(f"{k+'/'+lang:12} {c[k+':full']:>4} / {n:<4}({100*c[k+':full']/n:4.0f}%) {c[k+':part']:>4} / {n:<4} {c['traps_with_false_target']:>4} / {c['traps']:<4} {100*c['fp_visible']/c['texts']:8.1f} ({c['fp_visible']} in {c['texts']})")
# names: every mention in all EN/PL texts (other languages excluded)
for lang in ('EN','PL'):
    c=collections.Counter()
    for key,v in D.items():
        k,l=key.split('|')
        if l==lang: c.update(v)
    n=c['name']+c['side:name']; full=c['name:full']+c['side:name:full']
    print(f"names {lang}: all {full} / {n} ({100*full/n:.0f}%)", end='; ')
    for fm in ('forma:full','forma:single','forma:titled','forma:reversed','imie:seen','imie:unseen'):
        print(f"{fm.split(':')[1]} {c[fm+':full']} / {c[fm]}", end='; ')
    texts=c['texts']; fpn=c['fp_visible:name']
    print(f"| visible false [NAME]: {fpn} in {texts} texts = {100*fpn/texts:.1f}/100")
c=agg(lambda k,l: k=='name'); print('name traps (50 texts without a person): false [NAME] in', c['traps_with_false_target'],'/',c['traps'],'texts;',c['fp_trap_target'],'spans')
c=agg(lambda k,l: k=='inne')
print('OTHER LANGUAGES (60 DE/FR/ES/IT):', {x:(c['side:'+x+':full'],c['side:'+x]) for x in ('name','address','email','phone','iban','card')}, 'visible fp', c['fp_visible'], dict((k,v) for k,v in c.items() if k.startswith('fp_visible:')))
tot=collections.Counter()
for v in D.values(): tot.update(v)
print('ALL: texts',tot['texts'],'visible false masks', tot['fp_visible'], {k:v for k,v in tot.items() if k.startswith('fp_visible:')})
