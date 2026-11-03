"""Read-only current carrier/keeper detail for pack retention development."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/buttons-r31/candidate-d';O=Path(sys.argv[1]).resolve();O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'ButtonsR31.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));rows={}
def bounds(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
for o in D.Objects:
 if not any(n.lower()in o.Name.lower()for n in ['Pack','Tray','Battery','KeeperLongRail','SideRail','BottomRail','RailBridge','Riser','CarrierFloor','KeeperEndPlate']):continue
 if not hasattr(o,'Shape')or o.Shape.isNull():continue
 rows[o.Name]={'type':o.TypeId,'bounds_xyz_mm':bounds(o.Shape),'volume_mm3':o.Shape.Volume,'dependents':[q.Name for q in o.InList]}
meshes={}
for n in ['TipReadyCarrierR26','PCBOnlyKeeperR25','NarrowPackAllowance']:
 for suffix,s in [('',D.getObject(n).Shape),('-section',D.getObject(n).Shape.copy().common(Part.makeBox(100,150,100,A.Vector(-100,-20,-50))))]:
  p=O/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(p));meshes[p.name]=sha(p)
A.closeDocument(D.Name);assert sha(f)==before;(O/'source-inspection.json').write_text(json.dumps({'source_R31_native_sha256':before,'inspector_sha256':sha(Path(__file__)),'construction_features':rows,'source_role_meshes_sha256':meshes,'scope':'Read-only current source geometry and X<=0 sections; no design modification or fit acceptance.'},indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)
