"""Read-only alternative: published protected pack in unused flange wing.

No housing, PCB, motor or circuit edits; no battery selection.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'hardware/cad/pack-retention-r32/candidate-e'
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());f=P/'PackRetentionR32.FCStd'
before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f))
fixed={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])if not n.startswith('Pack')}
fixed['preserved_source_carrier_R26']=D.getObject('TipReadyCarrierR26').Shape.copy()
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
def hits(s):
 rows=[]
 for n,b in fixed.items():
  v=vol(s,b)
  if v>1e-5:rows.append({'fixed':n,'intersection_mm3':v})
 return rows
rows=[]
for x,y,z in itertools.product([7.,8.,9.,10.,11.],[-25.,-24.,-23.,-22.,-21.],[-1.,0.,1.]):
 pack=Part.makeBox(33,8,20,A.Vector(x,y,z-10))
 budget=Part.makeBox(34,9,21,A.Vector(x-.5,y-.5,z-10.5))
 ph=hits(pack);bh=hits(budget)
 row={'pack_min_xyz_mm':[x,y,z-10],'pack_XYZ_mm':[33,8,20],'pack_hits':ph,'budget_hits':bh,'clear':not ph and not bh};rows.append(row)
 print(x,y,z,'pack',ph,'budget',bh,'clear',row['clear'],flush=True)
out={'source_native_sha256':before,'screener_sha256':sha(Path(__file__)),'battery_selection':'OPEN','fixed_roles':list(fixed),'rows':rows,'clear_pose_count':sum(q['clear']for q in rows),'scope':'Static right-wing alternative vs unchanged housing, electronics, controls, hubs and existing harness allowances. Removes only R32 body-pack additions; preserves R26 carrier. Published20x33x8 protected reference and .5mm engineering sizing budget, not finished supplier maxima, leads/connector, expansion, holder, sensor support, routing, flange compliance or assembly acceptance.'}
(OUT/'pose-screen.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name);assert sha(f)==before
print('clear poses',out['clear_pose_count'],flush=True)
