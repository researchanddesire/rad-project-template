"""Export two cropped views of the saved R37 development assembly."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-assembly-r37';OUT=P/'display';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'power-f/geometry-report.json').read_text());p=P/'power-f/ConditionalPackPowerR37.FCStd';assert sha(p)==r['native_sha256'];D=A.openDocument(str(p));panels={}
specs=[('anchor',[-11,35.95,-11.8,5,36.05,-3.4],['PackAnchoredCarrierR37','PackWireSoftPadR37','PackTieSpaceR37','BodyPackPowerWireR37_1','SensorReturnCoatingR36','BodyPackPowerWireR37_2','PackConnectedWireR36_4','PackConnectedWireR36_5']),('power',[-42,-27,-17,42,-7,15],['PackPublishedGaugeR33','PackMateProcessSpaceR37']+[n for n in r['new_roles'] if n.startswith(('StockPackLeadR37_','SpareMateLeadR37_','BodyPackPowerWireR37_','PackPowerJointSpaceR37_'))]+['FactoryNTCWireR36_1_1','FactoryNTCWireR36_1_2','FactoryNTCWireR36_2_1','FactoryNTCWireR36_2_2','PackNTCHeadR33_1','PackNTCHeadR33_2'])]
for label,bounds,names in specs:
 x,y,z,u,v,w=bounds;clip=Part.makeBox(u-x,v-y,w-z,A.Vector(x,y,z));files={}
 for name in names:
  s=D.getObject(name).Shape.copy().common(clip.copy())
  if s.isNull()or s.Volume<1e-7:continue
  path=OUT/(name+'-'+label+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(path));files[path.name]=sha(path)
 panels[label]={'clip_xyz_mm':bounds,'meshes_sha256':files}
A.closeDocument(D.Name);assert sha(p)==r['native_sha256']
(OUT/'display-context.json').write_text(json.dumps({'native_sha256':sha(p),'exporter_sha256':sha(Path(__file__)),'panels':panels,'scope':'Clipped native geometry. Anchor view omits PCB and metal body; power view omits hubs, covers and boards for route visibility. All geometry remains in its installed pose. Conditional connector, shrink, wires and joints are engineering/process bounds.'},indent=2)+'\n');print('exported',sum(len(q['meshes_sha256'])for q in panels.values()),'meshes',flush=True)
