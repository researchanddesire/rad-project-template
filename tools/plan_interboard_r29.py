"""Ten independently swept candidate wires, from current native pin maps.

Coordinates at wire exits remain mating-envelope assumptions. Never infer an
approved finished harness, dynamic flex life or supplied wire tolerance here.
"""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SOURCE=ROOT/'hardware/pcb/flange-access-r28/candidate-s';CAD=ROOT/'hardware/cad/flange-controls-r27/candidate-d';i=json.loads((SOURCE/'layout-inspection.json').read_text());r=json.loads((CAD/'geometry-report.json').read_text())
j6=next(q for q in i['boards']['body']['placements']if q['ref']=='J6');j7=next(q for q in i['boards']['flange']['placements']if q['ref']=='J7')
def bez(p):return {'kind':'bezier5','poles_xyz_mm':np.array(p).tolist()}
def line(a,b):return bez([np.array(a)+(np.array(b)-a)*t for t in np.linspace(0,1,6)])
def arc(a,m,b,R):return {'kind':'circular_arc','start_xyz_mm':a,'mid_xyz_mm':m,'end_xyz_mm':b,'radius_mm':R}
def sample(seg):
 if seg['kind']=='bezier5':
  p=np.array(seg['poles_xyz_mm']);t=np.linspace(0,1,1001)[:,None]
  def ev(q):
   n=len(q)-1;return sum(math.comb(n,k)*t**k*(1-t)**(n-k)*v for k,v in enumerate(q))
  v=ev(p);d=ev(5*np.diff(p,axis=0));e=ev(20*np.diff(p,n=2,axis=0));cross=np.linalg.norm(np.cross(d,e),axis=1);mask=cross>1e-10;R=float(np.min(np.linalg.norm(d[mask],axis=1)**3/cross[mask]))if mask.any()else 1e12
  return v,R
 a,m,b=np.array([seg[k]for k in ['start_xyz_mm','mid_xyz_mm','end_xyz_mm']])
 # Quarter circles: midpoint determines orthogonal basis via endpoint chord.
 center=(a+b)/2+(a+b-2*m)/(2*(math.sqrt(2)-1));u=a-center;v=b-center;t=np.linspace(0,math.pi/2,1001)[:,None]
 assert abs(np.linalg.norm(u)-seg['radius_mm'])<1e-7 and abs(np.dot(u,v))<1e-7
 return center+np.cos(t)*u+np.sin(t)*v,seg['radius_mm']
rows=[];paths=[]
for pin in range(1,11):
 p=next(q for q in j6['pads']if q['n']==str(pin));q=next(q for q in j7['pads']if q['n']==str(pin));assert p['net']==q['net']
 col=((pin-1)//2-2)*.8;row=(pin-1)%2;z=.4+.9*row;x0=p['xy_mm'][0];xf=q['xy_mm'][0]+1.5
 a=[x0,26.375,2.1];b=[col,8,z];L=26.375-8;d=np.array([0,-L,0]);a=np.array(a);b=np.array(b)
 curves=[bez([a,a+d/5,a+2*d/5,b-2*d/5,b-d/5,b]),line(b,[col,-15.5,z])]
 R=8+col;y=-15.5-R
 curves.append(arc([col,-15.5,z],[-8+R/math.sqrt(2),-15.5-R/math.sqrt(2),z],[-8,y,z],R))
 curves.append(line([-8,y,z],[-10,y,z]));R=4.9-.9*row;xr=-10-R
 curves.append(arc([-10,y,z],[-10-R/math.sqrt(2),y,z+R-R/math.sqrt(2)],[xr,y,z+R],R))
 top=9+.8*row;curves.append(line([xr,y,z+R],[xr,y,top]));a=np.array([xr,y,top]);b=np.array([xf,-16.7125,8.3375]);d=np.array([0,0,24.])
 curves.append(bez([a,a+d/5,a+2*d/5,b+2*d/5,b+d/5,b]))
 samples=[sample(c)for c in curves];v=np.concatenate([s[0][:-1]for s in samples]+[samples[-1][0][-1:]]);paths.append(v)
 rows.append({'pin':pin,'net':p['net'],'start_xyz_mm':list(curves[0]['poles_xyz_mm'][0]),'end_xyz_mm':b.tolist(),'curves':curves,'wire_OD_allowance_mm':.6,'minimum_sampled_centerline_radius_mm':min(s[1]for s in samples),'sampled_path_length_mm':float(np.linalg.norm(np.diff(v,axis=0),axis=1).sum()),'maximum_sampled_Z_mm':float(v[:,2].max())})
 print(pin,p['net'],'R',rows[-1]['minimum_sampled_centerline_radius_mm'],'L',rows[-1]['sampled_path_length_mm'],'Zmax',rows[-1]['maximum_sampled_Z_mm'],flush=True)
gaps=[]
for n,a in enumerate(paths):
 for k,b in enumerate(paths[n+1:],n+1):gaps.append({'pins':[n+1,k+1],'sampled_surface_gap_mm':float(cKDTree(a).query(b)[0].min()-.6)})
result={'planner_sha256':sha(Path(__file__)),'source_current_native_board_sha256':{k:sha(SOURCE/k/(k+'-r28.kicad_pcb'))for k in ['body','flange']},'source_layout_inspection_sha256':sha(SOURCE/'layout-inspection.json'),'source_CAD_native_sha256':sha(CAD/'FlangeCradleR27.FCStd'),'wire_candidate':'Accu-Glass100690 28AWG stranded Kapton; catalogue OD.508nominal, no published OD tolerance; .6mm is a separate design allowance, not a maker maximum. Current radius.13in=3.302mm;4mm centerline target exceeds3.302+.3 if radius means inside.','wire_exit_basis':'J6 X and J7 X from native numbered pads; J7 transformedX+1.5. J6Y26.375/Z2.1 and J7Y-16.7125/Z8.3375 derive earlier conservative mating boxes/assumed wire centres, not controlled maker contact-egress datums. SHR-10V-S without protrusions 11mm width is required; B variant13mm is not substituted.','wires':rows,'sampled_wire_pair_gaps':gaps,'scope':'Exact Bezier/quarter-circle path definition and sampled radius/separation only. Candidate body-flange assembly routing; no static native fit, strain relief, service slack, actual finished cut length, dynamic flex, current/return/I2C/RF or physical acceptance.'}
(OUT/'wire-plan.json').write_text(json.dumps(result,indent=2)+'\n');print('min gap',min(g['sampled_surface_gap_mm']for g in gaps),flush=True)
