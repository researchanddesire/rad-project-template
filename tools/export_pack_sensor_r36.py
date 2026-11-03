"""Read-only native sensor wiring context and one bare-lap detail."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());path=P/'ConnectedPackSensorsR36.FCStd';before=sha(path);assert before==r['native_sha256']
D=A.openDocument(str(path));clip=Part.makeBox(55,22,30,A.Vector(-7,-30,-15));meshes={}
context=['PackPublishedGaugeR33','PackNTCHeadR33_1','PackNTCHeadR33_2']+r['new_roles']+[n for n in r['fixed_roles']if n.startswith(('NTCSpliceSpaceR36_','FactoryNTCWireR36_'))]
for name in context:
 if name in ['SensorReturnCoreR36','UpperSensorReturnCoreR36']or name.startswith(('FactoryLapBareR36_','PackAdapterBareR36_','NTCSolderBridgeR36_'))or name=='UpperSensorReturnBareR36':continue
 s=D.getObject(name).Shape.copy().common(clip.copy())
 if s.Volume<1e-7:continue
 p=P/(name+'-wiring.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.10,Relative=False).write(str(p));meshes[p.name]=sha(p)
detail=Part.makeBox(7.,3.,1.6,A.Vector(16.3,-15.93,-4.95));detail_meshes={}
for name in ['FactoryLapBareR36_1_2','PackAdapterBareR36_4','FactoryNTCWireR36_1_2','PackConnectedWireR36_4']:
 s=D.getObject(name).Shape.copy().common(detail.copy());assert s.isValid()and s.Volume>0
 p=P/(name+'-lap.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.008,AngularDeflection=.06,Relative=False).write(str(p));detail_meshes[p.name]=sha(p)
A.closeDocument(D.Name);assert sha(path)==before
(P/'display-context.json').write_text(json.dumps({'native_sha256':before,'exporter_sha256':sha(Path(__file__)),'wiring_clip_xyz_mm':[-7,-30,-15,48,-8,15],'wiring_meshes_sha256':meshes,'lap_clip_xyz_mm':[16.3,-15.93,-4.95,23.3,-12.93,-3.35],'lap_meshes_sha256':detail_meshes,'scope':'Actual native clipped wiring and bare-process geometry. Exterior/hubs omitted from overview; sleeve and solder omitted in lap detail. No fabricated source geometry or physical/process acceptance.'},indent=2)+'\n');print('exported',len(meshes),'wiring and',len(detail_meshes),'lap meshes',flush=True)
