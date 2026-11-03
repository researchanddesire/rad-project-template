"""Native Boolean pack-bay crop for review figures; no source changes."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'saved-review.json').read_text());f=P/'PackRetentionR32.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));a=D.getObject('PackRetainingCarrierR32').Shape.copy();crop=Part.makeBox(60,37.2,60,A.Vector(-30,33.8,-30));s=a.common(crop);cut=Part.makeBox(100,150,100,A.Vector(-100,-20,-50));meshes={}
for suffix,t in [('',s),('-section',s.copy().common(cut))]:
 assert t.isValid()and t.Volume>1
 out=P/('PackRetainingCarrierR32-close'+suffix+'.stl');MeshPart.meshFromShape(Shape=t,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(out));meshes[out.name]=sha(out)
A.closeDocument(D.Name);assert sha(f)==before;(P/'close-view-meshes.json').write_text(json.dumps({'native_sha256':before,'saved_review_sha256':sha(P/'saved-review.json'),'exporter_sha256':sha(Path(__file__)),'native_crop_bounds_xyz_mm':[-30,33.8,-30,30,71,30],'section':'X<=0','meshes_sha256':meshes,'scope':'Native Boolean display crop only; full source and mechanical review unchanged.'},indent=2)+'\n');print('Exported native pack-bay crop',flush=True)
