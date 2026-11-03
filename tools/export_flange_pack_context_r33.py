"""Read-only native flange PCB context and true cropped body for R33 figures."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=json.loads((P/'saved-review.json').read_text());f=P/'FlangePackR33.FCStd';before=sha(f);assert before==v['native_sha256'];D=A.openDocument(str(f));r=json.loads((P/'geometry-report.json').read_text());roles={n:D.getObject(n).Shape.copy()for n,q in r['parts'].items()if n.startswith('R17_')and q['bounds_xyz_mm'][1]<0};roles['BodyFlangeJunctionR33-display-crop']=D.getObject('KeyedBodyR25').Shape.copy().common(Part.makeBox(100,22,100,A.Vector(-50,-10,-50)));meshes={}
for n,s in roles.items():
 assert s.isValid()and s.Volume>0;p=P/(n+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(p));meshes[p.name]=sha(p)
clip=Part.makeBox(18,17,4,A.Vector(14,-28,-7));sensor_meshes={}
for n in r['new_roles']:
 s=D.getObject(n).Shape.copy().common(clip)
 if s.Volume<1e-7:continue
 assert s.isValid();p=P/(n+'-sensor-section.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(p));sensor_meshes[p.name]=sha(p)
A.closeDocument(D.Name);assert sha(f)==before;(P/'display-context.json').write_text(json.dumps({'native_sha256':before,'saved_review_sha256':sha(P/'saved-review.json'),'exporter_sha256':sha(Path(__file__)),'meshes_sha256':meshes,'sensor_section_meshes_sha256':sensor_meshes,'sensor_section_clip_xyz_mm':[14,-28,-7,32,-11,-3],'flange_component_count':len(roles)-1,'body_crop_bounds_xyz_mm':[-50,-10,-50,50,12,50],'scope':'Actual native whole flange-component boxes, Boolean body crop and one sensor longitudinal Boolean section only. No new fit acceptance.'},indent=2)+'\n');print('native context meshes',len(meshes),'sensor meshes',len(sensor_meshes),flush=True)
