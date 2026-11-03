"""Recompute the complete wire plan, including continuous numeric guards.

Derivative convex hulls bound curvature; sampling plus a Lipschitz allowance
bounds pair separation. These are guarded floating checks, not directed-rounding
proofs and not qualification of physical wire or moving harnesses.
"""
from pathlib import Path
import sys,json,hashlib,math,itertools
import numpy as np
from scipy.spatial import cKDTree
P=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True);r=json.loads(P.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();N=4000;GUARD=1e-9

def split(p):
 layers=[p]
 while len(layers[-1])>1:layers.append((layers[-1][:-1]+layers[-1][1:])/2)
 return np.array([v[0]for v in layers]),np.array([v[-1]for v in reversed(layers)])
def mul(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def bound(p,depth=0):
 L=2.**(-depth);d=5*np.diff(p,axis=0)/L;dd=4*np.diff(d,axis=0)/L;u=[(float(d[:,j].min())-GUARD,float(d[:,j].max())+GUARD)for j in range(3)];v=[(float(dd[:,j].min())-GUARD,float(dd[:,j].max())+GUARD)for j in range(3)];cross=[sub(mul(u[1],v[2]),mul(u[2],v[1])),sub(mul(u[2],v[0]),mul(u[0],v[2])),sub(mul(u[0],v[1]),mul(u[1],v[0]))];norm=sum(0 if a<=0<=b else min(abs(a),abs(b))**2 for a,b in u);k=math.sqrt(sum(max(abs(a),abs(b))**2 for a,b in cross))/norm**1.5 if norm>0 else math.inf
 if depth<7 or (k>1/4.0001 and depth<12):
  a,b=split(p);return max(bound(a,depth+1),bound(b,depth+1))
 return k

def sample(s):
 t=np.linspace(0,1,N+1)[:,None]
 if s['kind']=='bezier5':
  p=np.array(s['poles_xyz_mm'])
  def ev(q):
   n=len(q)-1;return sum(math.comb(n,k)*t**k*(1-t)**(n-k)*v for k,v in enumerate(q))
  d=5*np.diff(p,axis=0);e=4*np.diff(d,axis=0);v=ev(p);dv=ev(d);ddv=ev(e);cross=np.linalg.norm(np.cross(dv,ddv),axis=1);mask=cross>1e-10;R=float(np.min(np.linalg.norm(dv[mask],axis=1)**3/cross[mask]))if mask.any()else 1e12
  k=bound(p);lo=1/k if k else 1e12;return v,R,lo,float(np.linalg.norm(d,axis=1).max()),d[0],d[-1]
 a,m,b=np.array([s[k]for k in ['start_xyz_mm','mid_xyz_mm','end_xyz_mm']]);center=(a+b)/2+(a+b-2*m)/(2*(math.sqrt(2)-1));u=a-center;v=b-center;rad=s['radius_mm'];assert abs(np.linalg.norm(u)-rad)<1e-7 and abs(np.dot(u,v))<1e-7;t=t*math.pi/2
 return center+np.cos(t)*u+np.sin(t)*v,rad,rad,rad*math.pi/2,v,-u
paths=[];errors=[];rows=[]
for w in r['wires']:
 vals=[sample(s)for s in w['curves']];v=np.concatenate([x[0][:-1]for x in vals]+[vals[-1][0][-1:]]);paths.append(v);error=max(q[3]for q in vals)/(2*N)+1e-8;errors.append(error);joins=[]
 for a,b in zip(vals,vals[1:]):
  gap=float(np.linalg.norm(a[0][-1]-b[0][0]));cos=float(np.dot(a[-1],b[-2])/np.linalg.norm(a[-1])/np.linalg.norm(b[-2]));assert gap<1e-7 and cos>1-1e-9,(w['pin'],gap,cos);joins.append({'position_gap_mm':gap,'unit_tangent_dot':cos})
 w['minimum_sampled_centerline_radius_mm']=min(x[1]for x in vals);w['guarded_minimum_centerline_radius_mm']=min(x[2]for x in vals);w['sampled_path_length_mm']=float(np.linalg.norm(np.diff(v,axis=0),axis=1).sum());w['maximum_sampled_Z_mm']=float(v[:,2].max());w['maximum_point_sampling_error_mm']=error
 rows.append({'pin':w['pin'],'guarded_minimum_R_mm':w['guarded_minimum_centerline_radius_mm'],'all_joins_geometrically_tangent':joins,'point_error_bound_mm':error,'path_length_mm':w['sampled_path_length_mm']});print('pin',w['pin'],'R>=',w['guarded_minimum_centerline_radius_mm'],'length',w['sampled_path_length_mm'],flush=True)
gaps=[]
for i,a in enumerate(paths):
 tree=cKDTree(a)
 for j,b in enumerate(paths[i+1:],i+1):
  sampled=float(tree.query(b)[0].min()-.6);gaps.append({'pins':[i+1,j+1],'sampled_surface_gap_mm':sampled,'guarded_continuous_surface_gap_lower_mm':sampled-errors[i]-errors[j]})
accepted=all(q['guarded_minimum_R_mm']>=4 for q in rows)and all(q['guarded_continuous_surface_gap_lower_mm']>0 for q in gaps)
r['sampled_wire_pair_gaps']=gaps;r['complete_plan_reviewer_sha256']=sha(Path(__file__));r['search_plan_sha256']=sha(P);r['scope']='Exact stored degree5 Bezier/quarter-circle paths; guarded floating curvature and separation screens. No directed-rounding proof, static native fit/actual crimp/egress, restraint, service slack/motion, dynamic flex/electrical/physical acceptance.'
(OUT/'wire-plan.json').write_text(json.dumps(r,indent=2)+'\n');review={'source_search_plan_sha256':sha(P),'reviewed_plan_sha256':sha(OUT/'wire-plan.json'),'reviewer_sha256':sha(Path(__file__)),'samples_per_curve':N+1,'derivative_guard':GUARD,'all_curves_R_at_least_4mm_and_separated':accepted,'wires':rows,'pair_gaps':gaps,'scope':'Bernstein derivative-hull curvature bounds with adaptive subdivision through depth12; derivative interval expansion1e-9. Pair distance lower bounds use full-curve derivative-norm hull speed times half sample spacing for each curve (circular analytic speed), subtracted from nearest sample distance. Floating arithmetic, not a directed-rounding formal proof. No native/static, physical or dynamic-flex acceptance.'};(OUT/'plan-review.json').write_text(json.dumps(review,indent=2)+'\n');print('all geometry plan screens pass:',accepted,'min gap lower',min(q['guarded_continuous_surface_gap_lower_mm']for q in gaps),flush=True)
