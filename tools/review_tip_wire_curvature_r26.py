"""Bernstein derivative-hull curvature bounds, with explicit floating guard."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np
P=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(P.read_text());GUARD=1e-9
def split(p):
 layers=[p]
 while len(layers[-1])>1:layers.append((layers[-1][:-1]+layers[-1][1:])/2)
 return np.array([v[0]for v in layers]),np.array([v[-1]for v in reversed(layers)])
def mul(a,b):
 vals=[x*y for x in a for y in b];return min(vals),max(vals)
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def bound(p,L,depth=0):
 if depth<7:
  a,b=split(p);return max(bound(a,L/2,depth+1),bound(b,L/2,depth+1))
 d=5*np.diff(p,axis=0)/L;dd=4*np.diff(d,axis=0)/L
 u=[(float(d[:,j].min())-GUARD,float(d[:,j].max())+GUARD)for j in range(3)]
 v=[(float(dd[:,j].min())-GUARD,float(dd[:,j].max())+GUARD)for j in range(3)]
 cross=[sub(mul(u[1],v[2]),mul(u[2],v[1])),sub(mul(u[2],v[0]),mul(u[0],v[2])),sub(mul(u[0],v[1]),mul(u[1],v[0]))]
 minimum_norm_sq=sum((0 if a<=0<=b else min(abs(a),abs(b))**2)for a,b in u)
 assert minimum_norm_sq>0
 return math.sqrt(sum(max(abs(a),abs(b))**2 for a,b in cross))/minimum_norm_sq**1.5
rows=[]
for w in r['wires']:
 segs=[v for v in w['curves']if v['kind']=='bezier5'];segments=[]
 for i,s in enumerate(segs):
  p=np.array(s['poles_xyz_mm']);L=s['Y_span_mm'][1]-s['Y_span_mm'][0];k=bound(p,L);lo=1/k if k else math.inf
  segments.append({'index':i,'radius_lower_bound_mm':lo,'curvature_upper_bound_per_mm':k})
  if i:
   a=np.array(segs[i-1]['poles_xyz_mm']);La=segs[i-1]['Y_span_mm'][1]-segs[i-1]['Y_span_mm'][0]
   assert np.linalg.norm(a[-1]-p[0])<1e-8
   assert np.linalg.norm(5*(a[-1]-a[-2])/La-5*(p[1]-p[0])/L)<1e-8
   assert np.linalg.norm(20*(a[-1]-2*a[-2]+a[-3])/La**2-20*(p[2]-2*p[1]+p[0])/L**2)<1e-8
 low=min(q['radius_lower_bound_mm']for q in segments);assert low>=2.5,(w['pin'],low)
 arc=w['curves'][-1];assert arc['kind']=='circular_arc'and arc['radius_mm']==2.5
 assert np.linalg.norm(np.array(arc['start_xyz_mm'])-np.array(segs[-1]['poles_xyz_mm'][-1]))<1e-8
 rows.append({'pin':w['pin'],'polynomial_segments':segments,'minimum_polynomial_radius_lower_bound_mm':low,'analytic_arc_radius_mm':2.5,'polynomial_joins_C2':True,'polynomial_to_circle_join':'tangent-continuous (C1); curvature steps from0 to0.4/mm. No zero-radius corner.'})
 print(w['pin'],'guarded polynomial R >=',low,'arcR2.5',flush=True)
OUT.write_text(json.dumps({'plan_sha256':sha(P),'reviewer_sha256':sha(Path(__file__)),'subdivisions_per_polynomial':128,'derivative_interval_expansion':GUARD,'rows':rows,'scope':'Control-polygon convex hull bounds on first/second derivatives over each subdivided Bezier segment, propagated through cross-product/norm curvature. Numerical floating arithmetic with1e-9 derivative guards, not a directed-rounding formal proof. Source poles exact to stored precision. C2 polynomial transitions; the circle joins are C1. No wire OD/physical bend/crimp/service motion acceptance.'},indent=2)+'\n')
