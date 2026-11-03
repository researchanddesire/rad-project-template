"""Isolated pads through actual native metal, retaining the failed offset probe.

This does not move a connected harness, housing, PCB or carrier assembly.
"""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nf=P/'HarnessSupportR30.FCStd';before=sha(nf);r=json.loads((P/'geometry-report.json').read_text());review=json.loads((P/'saved-review.json').read_text());assert before==r['native_sha256']==review['native_sha256'];D=A.openDocument(str(nf));metal=D.getObject('KeyedBodyR25').Shape
rows=[]
for name,rot in [('CentralAnchorPadR30',A.Rotation()),('FlangeAnchorPadR30',A.Rotation(A.Vector(1,0,0),90))]:
 original=D.getObject(name).Shape;bb=original.optimalBoundingBox(False,False);center=A.Vector((bb.XMin+bb.XMax)/2,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2)
 for Z in [0.,1.]:
  for y in [45,30,20,10,0,-4,-8,-14]:
   s=original.copy();s.Placement=A.Placement(A.Vector(0,y,Z),rot).multiply(A.Placement(-center,A.Rotation())).multiply(s.Placement);b=s.optimalBoundingBox(False,False);v=s.copy().common(metal.copy()).Volume;dist=s.distToShape(metal)[0];rows.append({'pad':name,'center_Y_mm':y,'center_Z_mm':Z,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']],'metal_intersection_mm3':v,'metal_surface_distance_mm':dist});print(name,y,Z,'hit',v,'gap',dist,flush=True)
accepted=[q for q in rows if q['center_Z_mm']==0];out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'original_saved_review_sha256':sha(P/'saved-review.json'),'screener_sha256':sha(Path(__file__)),'center_basis':'Actual trimmed optimalBoundingBox. Supersedes the preserved loose BoundBox centering probe; cut-curve bounds can be inflated and offset.','rows':rows,'centered_poses_clear':all(q['metal_intersection_mm3']<1e-5 and q['metal_surface_distance_mm']>0 for q in accepted),'scope':'Actual native metal and isolated cured pad shape at listed poses. Flange pad rotatedX90 and held atX0/Z0 for centered passage; originalZ+1 failure is retained. No circular-bore assumption, connected harness/housing/carrier, hands, continuous motion, actual wire/overmold tolerances or physical assembly acceptance.'};(P/'transport-centering.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('centered clear',out['centered_poses_clear'],'minimum centered metal gap',min(q['metal_surface_distance_mm']for q in accepted),flush=True)
