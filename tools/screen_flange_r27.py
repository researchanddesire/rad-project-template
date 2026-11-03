"""Source-bound whole-island X90 flange placement screen against current R26."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/cad/tip-support-r26/candidate-f';OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True)
assert not any(OUT.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r=read(SRC/'geometry-report.json');nf=Path(sys.argv[1]).resolve();assert sha(nf)==r['native_sha256']
pcb=ROOT/'hardware/pcb/stackup-r23/candidate-d';inspection=read(pcb/'layout-inspection.json');f=inspection['boards']['flange']
assert sha(pcb/'flange/flange-r23.kicad_pcb')==f['native_board_sha256']
D=A.openDocument(str(nf));roles=['FlangePCB_R17']+['R17_'+p['ref']for p in f['placements']if p['body_xy_mm']]+['R17Mate_'+p['ref']for p in f['mates']]
base={n:D.getObject(n).Shape.copy()for n in roles};bb=Part.makeCompound(list(base.values())).BoundBox;center=A.Vector(bb.Center)
fixed={n:D.getObject(n).Shape for n in dict(r['parts'],**r['mates'],**r['allowances'])if n not in roles}
context=['FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference','HubLeft','HubRight','HubBolt_1','HubBolt1','HubNut_1','HubNut1','KeyedBodyR25']
def bounds(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
def volume(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
rows=[]
for x,y,z in [(0,0,0),(.5,0,0),(1,0,0),(1.5,0,0),(2,0,0),(.5,0,-.3),(1,0,-.3),(1.5,0,-.3),(1,1,-.3),(1.5,1,-.3)]:
 t=A.Placement(A.Vector(x,y,z)+center,A.Rotation(A.Vector(1,0,0),90)).multiply(A.Placement(-center,A.Rotation()))
 moving={}
 for n,s in base.items():
  v=s.copy();v.Placement=t.multiply(v.Placement);moving[n]=v
 hits=[]
 for n,s in moving.items():
  for m,v in fixed.items():
   q=volume(s,v)
   if q>1e-5:hits.append({'moving':n,'fixed':m,'intersection_mm3':q})
 gaps={n:min(s.distToShape(fixed[m])[0]for s in moving.values())for n,m in [(k,k)for k in context]}if not hits else {}
 b=bounds(Part.makeCompound(list(moving.values())))
 rows.append({'translation_xyz_mm':[x,y,z],'populated_bounds_xyz_mm':b,'populated_spans_xyz_mm':[b[i+3]-b[i]for i in range(3)],'intersections':hits,'minimum_island_to_context_gaps_mm':gaps})
 print('X90 offset',[x,y,z],'hits',hits,'gaps',gaps,flush=True)
out={'native_R26_sha256':sha(nf),'geometry_report_sha256':sha(SRC/'geometry-report.json'),'flange_native_sha256':f['native_board_sha256'],'PCB_inspection_sha256':sha(pcb/'layout-inspection.json'),'screener_sha256':sha(Path(__file__)),'rotation_center_xyz_mm':list(center),'moving_roles':roles,'fixed_roles':list(fixed),'context_roles':context,'cases':rows,'scope':'Rigid island placement screen only against all current primary/mate/allowance roles; measured nearest gaps to ten fixed context roles. Current exterior untouched. No support, buttons, wire/flex, RF, assembly motion, received tolerance or physical acceptance.'}
(OUT/'orientation-screen.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name)
assert sha(nf)==r['native_sha256']
