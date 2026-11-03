"""Diagnostico reproduzivel (somente leitura). Uso: python scripts/diagnostico/serie_chamados_inversao_datas.py <caminho para malha-ia/dados/chamados.json>

Datas lidas como AAAA-MM-DD, sem inversao de dia e mes.
"""
import sys
CAMINHO_CHAMADOS = sys.argv[1] if len(sys.argv) > 1 else "../malha-ia/dados/chamados.json"
import json,re,collections,numpy as np
rows=json.load(open(CAMINHO_CHAMADOS, encoding='utf-8'))
cor=collections.Counter(); sw=collections.Counter(); camp=collections.defaultdict(collections.Counter)
for r in rows[1:]:
    m=re.match(r'(\d{4})-(\d{2})-(\d{2})',str(r[2]))
    if not m: continue
    y,mo,d=map(int,m.groups()); cor[(y,mo)]+=1; camp[r[7]][(y,mo)]+=1
    sw[(y,mo) if d>12 else (y,d)]+=1
idx=[];y,m=2015,6
while (y,m)<=(2026,9):
    idx.append((y,m)); m+=1
    if m>12:y+=1;m=1
def arr(c,start=(2015,6)): return np.array([c.get(k,0) for k in idx],float)
a=arr(cor); b=arr(sw)
print('n meses',len(a),'ate 2026-09 (outubro 2026 excluido por ser corrente)')
print('soma cor',a.sum(),'soma swap',b.sum())
print('MAE |cor-swap| 2018+',np.abs(a-b)[31:].mean().round(2),'max',np.abs(a-b)[31:].max())
def stats(x,nome,ini):
    s=x[ini:]; mu=s.mean(); v=s.var(ddof=1)
    def acf(k): s0=s-mu; return (s0[k:]*s0[:-k]).sum()/(s0**2).sum()
    print(nome,'n',len(s),'media',mu.round(1),'var',v.round(0),'var/media',(v/mu).round(1),'CV',(s.std(ddof=1)/mu).round(2),'ACF1',acf(1).round(2),'ACF12',acf(12).round(2),'zeros',int((s==0).sum()))
i2018=idx.index((2018,1)); i2021=idx.index((2021,1))
for x,n in ((a,'correta 2018+'),(b,'swap 2018+')): stats(x,n,i2018)
for x,n in ((a,'correta 2021+'),(b,'swap 2021+')): stats(x,n,i2021)
# perfil sazonal 2021-2025 (anos completos)
prof=np.zeros(12)
for mo in range(1,13): prof[mo-1]=np.mean([cor[(yy,mo)] for yy in range(2021,2026)])
print('perfil sazonal correto 2021-2025',prof.round(0).tolist())
prof2=np.zeros(12)
for mo in range(1,13): prof2[mo-1]=np.mean([sw[(yy,mo)] for yy in range(2021,2026)])
print('perfil sazonal swap 2021-2025   ',prof2.round(0).tolist())
# rolling origin baselines: 24 origens finais, h=1..12
def ro(x,start_train=i2018,nor=24,H=12):
    res=collections.defaultdict(list)
    n=len(x)
    for o in range(n-H-nor+1,n-H+1):
        tr=x[start_train:o]; te=x[o:o+H]
        f={'naive':np.repeat(tr[-1],H),'sazonal_naive':tr[-12:][:H] if len(tr)>=12 else np.repeat(tr[-1],H),'media12':np.repeat(tr[-12:].mean(),H),'media_hist':np.repeat(tr.mean(),H)}
        for k,v in f.items(): res[k].append(te-v)
    out={}
    for k,v in res.items():
        e=np.concatenate(v); out[k]=(np.abs(e).mean().round(1),np.sqrt((e**2).mean()).round(1))
    return out
print('RO baselines (MAE,RMSE) serie correta',ro(a)); print('RO baselines serie swap',ro(b))
# por campus: mediana mensal 2021+
for c,cc in camp.items():
    s=np.array([cc.get(k,0) for k in idx])[i2021:]
    print(c,'media mensal 2021+',s.mean().round(1),'zeros',int((s==0).sum()))
