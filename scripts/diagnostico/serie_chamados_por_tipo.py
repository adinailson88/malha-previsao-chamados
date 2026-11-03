"""Diagnostico reproduzivel (somente leitura). Uso: python scripts/diagnostico/serie_chamados_por_tipo.py <caminho para malha-ia/dados/chamados.json>

Datas lidas como AAAA-MM-DD, sem inversao de dia e mes.
"""
import sys
CAMINHO_CHAMADOS = sys.argv[1] if len(sys.argv) > 1 else "../malha-ia/dados/chamados.json"
import json,re,collections,numpy as np
rows=json.load(open(CAMINHO_CHAMADOS, encoding='utf-8'))
cats=collections.Counter(); ser=collections.defaultdict(collections.Counter)
for r in rows[1:]:
    m=re.match(r'(\d{4})-(\d{2})',str(r[2]))
    if not m: continue
    c=str(r[12]).strip(); t=c.split('>')[0].split('-')[0].strip()[:40] if c else '(vazio)'
    cats[t]+=1; ser[t][(int(m.group(1)),int(m.group(2)))]+=1
print(cats.most_common(8))
print([str(r[12]) for r in rows[1:200] if r[12]][:6])
idx=[(y,m) for y in range(2018,2027) for m in range(1,13) if (y,m)<=(2026,9)]
for t,_ in cats.most_common(4):
    s=np.array([ser[t].get(k,0) for k in idx],float); mu=s.mean(); s0=s-mu
    ac=lambda k:(s0[k:]*s0[:-k]).sum()/(s0**2).sum()
    print(t,'media',mu.round(1),'var/media',(s.var(ddof=1)/mu).round(1),'ACF1',ac(1).round(2),'ACF12',ac(12).round(2),'anual',[int(sum(v for (y,_),v in ser[t].items() if y==yy)) for yy in range(2018,2027)])
# status e preenchimento
print('desc vazia',sum(1 for r in rows[1:] if r[2] and not r[22]))
