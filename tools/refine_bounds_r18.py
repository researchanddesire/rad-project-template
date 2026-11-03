"""Correct report bounding metadata using native tight bounds; no CAD edits."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=P/'PCBIntegrationR18.FCStd';rp=P/'geometry-report.json';r=json.loads(rp.read_text());before=sha(f);assert before==r['native_sha256'];d=A.openDocument(str(f));old=rp.read_bytes();changes={}
for domain in ['parts','mates']:
 for n,v in r[domain].items():
  s=d.getObject(n).Shape;b=s.optimalBoundingBox(False,False);bounds=[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']];assert s.isValid()==v['valid']and len(s.Solids)==v['solids']and abs(s.Volume-v['volume_mm3'])<1e-4
  if max(abs(a-b)for a,b in zip(bounds,v['bounds_xyz_mm']))>1e-5:changes[n]={'original_conservative_bounds_xyz_mm':v['bounds_xyz_mm'],'tight_native_bounds_xyz_mm':bounds}
  v['bounds_xyz_mm']=bounds
A.closeDocument(d.Name);assert sha(f)==before;(P/'geometry-before-tight-bounds.json').write_bytes(old);r['tight_bounds_metadata_correction']={'tool_sha256':sha(Path(__file__)),'native_unchanged_sha256':before,'original_report_sha256':hashlib.sha256(old).hexdigest(),'changes':changes,'reason':'Generic Shape.BoundBox can include spline control bounds and change after native reload/recompute. Use optimalBoundingBox(False,False) consistently. Volumes, solids and native CAD unchanged; original conservative AABB broad-phase could only add candidate pairs.'};rp.write_text(json.dumps(r,indent=2)+'\n');print(len(changes),'tight native bounds corrected; native unchanged',flush=True)
