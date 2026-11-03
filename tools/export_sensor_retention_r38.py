"""Export actual R38 comb context and one native section through four laps."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/joint-retention-r38/sensor-c';OUT=P/'display';OUT.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());path=P/'RetainedSensorJointsR38.FCStd';assert sha(path)==r['native_sha256'];D=A.openDocument(str(path));panels={}
context=[n for n in r['new_roles']if n!='JointRetainingHubR38']+['SensorReturnYJointR36']+[n for n in r['fixed_roles']if n.startswith(('NTCSpliceSpaceR36_','FactoryNTCWireR36_','PackNTCHeadR33_'))]+['UpperSensorReturnCoatingR36']
section=['JointRetainingHubR38','SensorJointCombR38','JointCombScrewEnvelopeR38']+[n for n in r['new_roles']if n.startswith('JointCombSoftPadR38_')]+[n for n in r['fixed_roles']if n.startswith('NTCSpliceSpaceR36_')]
for label,bounds,names in [('context',[9,-16,-8,33,-9,16],context),('section',[19.75,-16,-7.4,19.85,-9,9],section)]:
 x,y,z,u,v,w=bounds;clip=Part.makeBox(u-x,v-y,w-z,A.Vector(x,y,z));files={}
 for n in names:
  s=D.getObject(n).Shape.copy().common(clip.copy())
  if s.isNull()or s.Volume<1e-7:continue
  p=OUT/(n+'-'+label+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False).write(str(p));files[p.name]=sha(p)
 panels[label]={'clip_xyz_mm':bounds,'meshes_sha256':files}
A.closeDocument(D.Name);assert sha(path)==r['native_sha256'];(OUT/'display-context.json').write_text(json.dumps({'native_sha256':sha(path),'exporter_sha256':sha(Path(__file__)),'panels':panels,'scope':'Actual native installed pose. Context omits hub, pack, covers and boards; section is0.10mm thick through X19.8. Joint/pad/screw geometry remains engineering/process budgets, not received parts.'},indent=2)+'\n');print('exported R38 context and section',flush=True)
