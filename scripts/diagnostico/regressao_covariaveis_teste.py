"""Diagnostico reproduzivel (somente leitura). Uso: python scripts/diagnostico/regressao_covariaveis_teste.py <caminho para malha-ia/dados/chamados.json>

Datas lidas como AAAA-MM-DD, sem inversao de dia e mes.
"""
import sys
CAMINHO_CHAMADOS = sys.argv[1] if len(sys.argv) > 1 else "../malha-ia/dados/chamados.json"
import json,collections,numpy as np
rows=[r for r in json.load(open(CAMINHO_CHAMADOS, encoding='utf-8'))[1:] if r[2]]
idx=[(y,m) for y in range(2018,2027) for m in range(1,13) if (y,m)<=(2026,9)]
N=collections.Counter();C=collections.Counter();CP=collections.Counter()
for r in rows:
    k=(int(r[2][:4]),int(r[2][5:7])); N[k]+=1; v=float(r[16] or 0); C[k]+=v
    if str(r[12]).startswith('Posto de trabalho'): CP[k]+=v
n=np.array([N[k] for k in idx],float); c=np.array([C[k] for k in idx]); cs=c-np.array([CP[k] for k in idx])
mon=np.array([k[1] for k in idx]); t=np.arange(len(idx),dtype=float)
letivo=np.array([1.0 if (3<=m<=6 or 8<=m<=12) else 0.0 for m in mon])
rng=np.random.default_rng(1); chuva_sint=rng.uniform(30,250,len(idx))
def X(cols,sl): return np.column_stack([np.ones(len(t))]+cols)[sl]
def ro(y,cols_fn,nor=24,H=12,log=True,start=0):
    e=[];eb=[]
    for o in range(len(y)-H-nor+1,len(y)-H+1):
        tr=slice(start,o); te=slice(o,o+H); Xf=cols_fn()
        A=np.column_stack([np.ones(len(y))]+Xf)
        yt=np.log1p(y) if log else y
        b=np.linalg.lstsq(A[tr],yt[tr],rcond=None)[0]; p=A[te]@b
        p=np.expm1(p) if log else p
        e.append(y[te]-p); eb.append(y[te]-y[tr].mean())
    f=lambda x:(round(float(np.abs(np.concatenate(x)).mean()),1),round(float(np.sqrt(np.mean(np.concatenate(x)**2))),1))
    return f(e),f(eb)
mdum=[ (mon==m).astype(float) for m in range(2,13)]
print('CONTAGEM  (OLS em log1p; MAE,RMSE) modelo | media historica')
print(' tendencia            ',ro(n,lambda:[t]))
print(' letivo               ',ro(n,lambda:[letivo]))
print(' letivo+tendencia     ',ro(n,lambda:[letivo,t]))
print(' mes (dummies)        ',ro(n,lambda:mdum))
print(' letivo+chuva sintet. ',ro(n,lambda:[letivo,chuva_sint]))
print('CUSTO total (oraculo N): log1p(custo) ~')
print(' logN                 ',ro(c,lambda:[np.log(n)]))
print(' logN+letivo+tend     ',ro(c,lambda:[np.log(n),letivo,t]))
print(' sem N: letivo+tend   ',ro(c,lambda:[letivo,t]))
print('CUSTO sem Posto:')
print(' logN                 ',ro(cs,lambda:[np.log(n)]))
print(' logN+letivo+tend     ',ro(cs,lambda:[np.log(n),letivo,t]))
print(' sem N: letivo+tend   ',ro(cs,lambda:[letivo,t]))
print('corr(log custo sem Posto, log N)',np.corrcoef(np.log1p(cs),np.log(n))[0,1].round(2),'| corr(N,custo)',np.corrcoef(n,cs)[0,1].round(2))
# painel campus
camp=collections.defaultdict(collections.Counter)
for r in rows: camp[r[7]][(int(r[2][:4]),int(r[2][5:7]))]+=1
for k in ('Campus Jorge Amado','Campus Paulo Freire','Campus Sosígenes Costa','Reitoria'):
    s=np.array([camp[k].get(i,0) for i in idx],float); print(k,'media',s.mean().round(1),'CV',(s.std(ddof=1)/s.mean()).round(2),'corr com total',np.corrcoef(s,n)[0,1].round(2))
