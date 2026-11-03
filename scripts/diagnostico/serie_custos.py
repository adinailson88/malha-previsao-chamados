"""Diagnostico reproduzivel (somente leitura). Uso: python scripts/diagnostico/serie_custos.py <caminho para malha-ia/dados/chamados.json>

Datas lidas como AAAA-MM-DD, sem inversao de dia e mes.
"""
import sys
CAMINHO_CHAMADOS = sys.argv[1] if len(sys.argv) > 1 else "../malha-ia/dados/chamados.json"
import json,re,collections,numpy as np
rows=json.load(open(CAMINHO_CHAMADOS, encoding='utf-8'))[1:]
def pv(v):
    if v in (None,''): return None
    if isinstance(v,(int,float)): return float(v) if v>=0 else None
    s=str(v).replace('R$','').replace(' ','').strip()
    if ',' in s and '.' in s: s=s.replace('.','').replace(',','.')
    elif ',' in s: s=s.replace(',','.')
    try:
        x=float(s); return x if x>=0 else None
    except: return None
tipos=collections.Counter(type(r[16]).__name__ for r in rows if r[2]); print('tipos col16',tipos)
print('amostras',[r[16] for r in rows if r[2] and r[16]!=''][:8])
com=[r for r in rows if r[2]]
val=[(r,pv(r[16])) for r in com]
pos=[(r,v) for r,v in val if v and v>0]
print('chamados',len(com),'com valor>0',len(pos),round(100*len(pos)/len(com),1),'%','valor zero',sum(1 for r,v in val if v==0),'vazio/inval',sum(1 for r,v in val if v is None))
tot=sum(v for r,v in pos); print('soma R$',round(tot))
vs=np.array([v for r,v in pos]); print('quantis',np.percentile(vs,[0,25,50,75,90,99,100]).round(0), 'top1% share',round(np.sort(vs)[-len(vs)//100:].sum()/vs.sum(),3),'top10 share',round(np.sort(vs)[-10:].sum()/vs.sum(),3))
by=collections.defaultdict(lambda:[0,0,0.0])
for r,v in val:
    y=int(r[2][:4]); by[y][0]+=1
    if v and v>0: by[y][1]+=1; by[y][2]+=v
for y in sorted(by): print(y,by[y][0],by[y][1],round(100*by[y][1]/by[y][0]),'%',round(by[y][2]))
def cat(r): return str(r[12]).split('>')[0].strip()
pc=collections.defaultdict(lambda:[0,0,0.0])
for r,v in val:
    c=cat(r); pc[c][0]+=1
    if v and v>0: pc[c][1]+=1; pc[c][2]+=v
for c,a in sorted(pc.items(),key=lambda x:-x[1][0])[:7]: print(c,a[0],a[1],round(100*a[1]/a[0]),'%',round(a[2]))
# serie mensal correta (ISO) e invertida
def serie(swap):
    s=collections.defaultdict(float); n=collections.Counter()
    for r,v in pos:
        y,m,d=map(int,r[2][:10].split('-'))
        k=(y,d) if (swap and d<=12) else (y,m); s[k]+=v; n[k]+=1
    return s,n
idx=[(y,m) for y in range(2018,2027) for m in range(1,13) if (y,m)<=(2026,9)]
sc,nc=serie(False); ss,_=serie(True)
a=np.array([sc.get(k,0) for k in idx]); b=np.array([ss.get(k,0) for k in idx]); n=np.array([nc.get(k,0) for k in idx])
print('meses com custo zero 2018+',int((a==0).sum()),'de',len(a)); print('serie correta (R$ mil):',(a/1000).round(0).astype(int).tolist())
print('media',a.mean().round(0),'dp',a.std(ddof=1).round(0),'CV',(a.std(ddof=1)/a.mean()).round(2),'max/mediana',(a.max()/np.median(a)).round(1))
for nome,x in (('correta',a),('invertida',b)):
    x0=x-x.mean(); ac=lambda k:(x0[k:]*x0[:-k]).sum()/(x0**2).sum(); print(nome,'ACF1',ac(1).round(2),'ACF12',ac(12).round(2),'CV',(x.std(ddof=1)/x.mean()).round(2))
print('log: CV de log(1+x)',np.log1p(a).std(ddof=1).round(2))
print('custo medio por chamado com valor (R$) por ano', {y:round(by[y][2]/by[y][1]) for y in sorted(by) if by[y][1]})
print('corr(custo,n) mensal',np.corrcoef(a,n)[0,1].round(2))
# maior mes e maior chamado
i=a.argmax(); print('mes max',idx[i],a[i].round(0),'maior chamado no mes', max(v for r,v in pos if r[2][:7]==f'{idx[i][0]}-{idx[i][1]:02d}'))
# baselines RO
def ro(x,st=0,nor=24,H=12):
    res=collections.defaultdict(list)
    for o in range(len(x)-H-nor+1,len(x)-H+1):
        tr=x[st:o]; te=x[o:o+H]
        f={'naive':np.repeat(tr[-1],H),'media12':np.repeat(tr[-12:].mean(),H),'mediana12':np.repeat(np.median(tr[-12:]),H),'media_hist':np.repeat(tr.mean(),H)}
        for k,v in f.items(): res[k].append(te-v)
    return {k:(round(float(np.abs(np.concatenate(v)).mean())),round(float(np.sqrt((np.concatenate(v)**2).mean())))) for k,v in res.items()}
print('RO custo correta',ro(a)); print('RO custo invertida',ro(b))
