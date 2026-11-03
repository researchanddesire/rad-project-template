"""Bounded numerical search of the ten flange loops, preserving endpoints.

Sampled bend and separation constraints only; native static checks follow.
"""
from pathlib import Path
import sys,json,math,hashlib
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
P=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True);seed=json.loads(P.read_text());n=10;ts=np.linspace(0,1,241)
def matrix(deg,t):return np.array([math.comb(deg,k)*t**k*(1-t)**(deg-k)for k in range(deg+1)]).T
B=matrix(5,ts);D=matrix(4,ts);E=matrix(3,ts)
base=np.array([q['curves'][-1]['poles_xyz_mm']for q in seed['wires']]);baseL=24.
def polys(x):
 p=base.copy();alpha=x[:10];beta=x[10:20];length=x[20:]
 for i in range(n):
  a,b=p[i,0].copy(),p[i,5].copy();d=np.array([0,0,length[i]])
  p[i]=[a,a+d/5,a+2*d/5,b+2*d/5,b+d/5,b];p[i,2,1]+=alpha[i];p[i,3,1]+=beta[i]
 return p
def evaluate(x,full=False):
 p=polys(x);v=np.einsum('ts,isk->itk',B,p);d=np.einsum('ts,isk->itk',D,5*np.diff(p,axis=1));e=np.einsum('ts,isk->itk',E,20*np.diff(p,n=2,axis=1));cross=np.linalg.norm(np.cross(d,e),axis=2);r=np.linalg.norm(d,axis=2)**3/np.maximum(cross,1e-10)
 trees=[cKDTree(a)for a in v];gaps=np.array([trees[i].query(v[j])[0].min()for i in range(n)for j in range(i+1,n)])
 if full:return p,v,r,gaps
 # Keep loops apart with 0.1mm reserve over OD allowance; and R>=4.02.
 res=list(10*np.minimum(gaps-.70,0));res.extend((3*np.minimum(r.min(axis=1)-4.02,0)).tolist());res.extend((2*np.maximum(v[:,:,2].max(axis=1)-17.0,0)).tolist());res.extend((2*np.maximum(v[:,:,1].max(axis=1)+5,0)).tolist());res.extend((2*np.minimum(v[:,:,1].min(axis=1)+25.15,0)).tolist());res.extend((.0002*x).tolist());return np.array(res)
best=None;rng=np.random.default_rng(29)
for attempt in range(8):
 x=np.r_[np.tile([4.,-4.],5),np.tile([4.,-4.],5),np.repeat(24.,10)]if attempt==0 else np.r_[rng.uniform(-5,5,20),rng.uniform(21,25,10)]
 out=least_squares(evaluate,x,bounds=(np.r_[np.repeat(-7,20),np.repeat(18,10)],np.r_[np.repeat(7,20),np.repeat(26,10)]),max_nfev=240,ftol=1e-9,xtol=1e-9,gtol=1e-9)
 p,v,r,g=evaluate(out.x,True);score=float(np.square(evaluate(out.x)[:-30]).sum());print(attempt,'cost',score,'gap',g.min()-.6,'R',r.min(),'Z',v[:,:,2].max(),flush=True)
 if best is None or score<best[0]:best=(score,out.x,p,v,r,g)
 if g.min()>.69 and r.min()>4 and v[:,:,2].max()<17.05:break
score,x,p,v,r,g=best;result=dict(seed);result['loop_search']={'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed_plan_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'parameters':x.tolist(),'sampled_minimum_surface_gap_mm':float(g.min()-.6),'sampled_minimum_loop_radius_mm':float(r.min()),'sampled_maximum_Z_mm':float(v[:,:,2].max()),'cost':score,'scope':'No native or continuous geometry acceptance; original plan rest-of-route unchanged. Native per-wire and all-source screens required.'}
for i,q in enumerate(result['wires']):q['curves'][-1]['poles_xyz_mm']=p[i].tolist()
(OUT/'wire-plan-search.json').write_text(json.dumps(result,indent=2)+'\n')
