"""Full generic calibration shaft up to the stop face at three settings.

Supplements the shorter shaft in assembly-screen.json; no actual socket/key
engagement is modeled. Boot/bezel wait during adjustment.
"""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());nf=P/'ButtonsR31.FCStd';before=sha(nf);assert before==r['native_sha256'];D=A.openDocument(str(nf));shapes={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])};rows=[]
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
for q in r['button_spec']:
 ref=q['switch'];x,z=q['center_XZ_mm'];name='ButtonStopScrewR31_'+ref
 for travel in [.05,.58,.95]:
  end=-27.7+travel;probe=Part.makeCylinder(.65,end+42,A.Vector(x,-42,8),A.Vector(0,1,0));stop=shapes[name].copy();stop.translate(A.Vector(0,travel-q['study_stop_stroke_mm'],0));bad=[]
  for n,b in shapes.items():
   if n in {'ButtonBootR31','ButtonBezelR31',name}:continue
   v=vol(probe,b)
   if v>1e-5:bad.append({'fixed':n,'intersection_mm3':v})
  gap=probe.distToShape(stop)[0];overlap=vol(probe,stop);assert gap<1e-6 and overlap<1e-5,(ref,travel,gap,overlap);rows.append({'switch':ref,'adjustment_study_mm':travel,'shaft_diameter_mm':1.3,'shaft_Y_start_end_mm':[-42,end],'repositioned_own_stop_face_gap_mm':gap,'own_stop_intersection_mm3':overlap,'unexpected_hits':bad})
A.closeDocument(D.Name);assert sha(nf)==before
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'reviewer_sha256':sha(Path(__file__)),'full_face_access_probes':rows,'all_listed_shafts_clear_to_stop_face':not any(q['unexpected_hits']for q in rows),'scope':'Full straight shaft through arm to repositioned socket-end face at .05/.58/.95mm settings, with boot/bezel absent. Supplements shorter shafts in assembly-screen. No supplier drive/key/socket engagement or hand access; travel settings are geometry only.'};(P/'calibration-access-review.json').write_text(json.dumps(out,indent=2)+'\n');print(out['all_listed_shafts_clear_to_stop_face'],rows,flush=True)
