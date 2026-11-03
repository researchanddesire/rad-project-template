"""Read-only independent native-history, parameter, waist and STEP screen.

Run with FreeCAD bundled Python. This does not replay the generator or
qualify physical assembly, materials, sealing, loads or operating behavior.
"""
from pathlib import Path
import sys,json,hashlib,math
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
p=Path(__file__).resolve().parents[1]/'hardware/cad/prototype-r2'
rp=p/'geometry-report.json';f=p/'ButtplugPrototypeR2.FCStd'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
r=json.loads(rp.read_text());original=sha(f);report_hash=sha(rp)
assert original==r['native_sha256'],'Native/report mismatch before independent read'
doc=App.openDocument(str(f));snap={n:doc.getObject(n).Shape.copy() for n in r['parts']}
for o in doc.Objects:o.touch()
doc.recompute();parts={}
for n,e in r['parts'].items():
 s=doc.getObject(n).Shape;b=s.BoundBox
 bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
 q={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'volume_difference_mm3':s.Volume-e['volume_mm3'],'max_bound_difference_mm':max(abs(x-y) for x,y in zip(bounds,e['bounds_xyz_mm']))}
 assert q['valid'] and q['solids']==e['solids'],(n,q)
 assert abs(q['volume_difference_mm3'])<1e-4 and q['max_bound_difference_mm']<1e-5,(n,q)
 parts[n]=q
clip=Part.makeBox(80,.1,80,App.Vector(-40,10,-40))
metal=Part.makeCompound([doc.getObject(n).Shape for n in ['MetalShellLower','MetalShellUpper','FemaleNoseCap']])
neck=Part.makeCompound([doc.getObject(n).Shape.common(clip) for n in ['MetalShellLower','MetalShellUpper']])
board=doc.getObject('TBoardReservation').Shape.common(clip);bb=neck.BoundBox;pb=board.BoundBox
assert abs(bb.XLength-15)<1e-5 and abs(bb.ZLength-15)<1e-5
assert abs(pb.XLength-8)<1e-5 and abs(pb.ZLength-1)<1e-5
assert abs(neck.Volume/.1-math.pi*(7.5**2-6**2))<1e-4
outside=metal.cut(Part.makeCylinder(37.338/2,150,App.Vector(0,-20,0),App.Vector(0,1,0))).Volume
assert outside<1e-5,outside
step=Part.Shape();step.read(str(p/'ButtplugPrototypeR2.step'));assert step.isValid()
param=json.loads((p/'parameters.json').read_text());sheet=doc.getObject('Parameters');sheet_check={}
for k,v in param.items():
 if type(v) not in (float,int):continue
 try:
  a=getattr(sheet,k);actual=float(a.Value) if hasattr(a,'Value') else float(a)
 except Exception as exc:sheet_check[k]={'missing_or_unreadable':str(exc)};continue
 sheet_check[k]={'native_mm':actual,'json_mm':v,'matches':abs(actual-v)<1e-8}
assert all(x.get('matches') for x in sheet_check.values()),sheet_check
App.closeDocument(doc.Name)
assert sha(f)==original and sha(rp)==report_hash,'Source changed during independent read'
result={'status':'PASS_saved_native_history_and_envelope_screen_only','native_sha256':original,'geometry_report_sha256':report_hash,'method':'Independent saved-document reopen, touch every object and force full feature-history recompute without save. Named final validity/solid/volume/bounds compare; exact waist section; metal enclosing cylinder; native numeric spreadsheet versus current JSON; STEP read. Does not replay generator or accept unresolved assembly collisions.','parts':parts,'waist_slice':{'outer_x_mm':bb.XLength,'outer_z_mm':bb.ZLength,'board_width_mm':pb.XLength,'board_thickness_mm':pb.ZLength,'bare_board_clearance_mm':board.distToShape(neck)[0],'board_metal_overlap_mm3':board.common(neck).Volume},'metal_outside_37_338_diameter_mm3':outside,'combined_step_valid':step.isValid(),'combined_step_solids':len(step.Solids),'spreadsheet':sheet_check,'reported_remaining_intersections':r.get('unintended_intersections',[]),'scope':'Functional development checkpoint only. Remaining intersections and loading/interface gates are not cleared by a valid native model. No selected battery, physical assembly, strength, seal, materials, electrical operation, comfort or wear qualification.'}
(p/'independent-full-native-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['parts','spreadsheet','reported_remaining_intersections']},indent=2))
