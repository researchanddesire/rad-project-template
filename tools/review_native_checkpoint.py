"""Read-only independent saved-history, waist and STEP checkpoint review."""
from pathlib import Path
import argparse, hashlib, json, math, sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part

a=argparse.ArgumentParser(description=__doc__)
a.add_argument('directory',type=Path);a.add_argument('--native',required=True)
a.add_argument('--step',required=True);a.add_argument('--expected-sha',required=True)
a.add_argument('--shell-lower',default='MetalShellLower')
a.add_argument('--shell-upper',default='MetalShellUpper')
a.add_argument('--pcb',default='TBoardReservation')
args=a.parse_args();p=args.directory.resolve();f=p/args.native;rp=p/'geometry-report.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(rp.read_text());before=sha(f);report_sha=sha(rp)
assert before==args.expected_sha==r['native_sha256']
d=App.openDocument(str(f))
for o in d.Objects:o.touch()
d.recompute();parts={}
for n,e in r['parts'].items():
    s=d.getObject(n).Shape;b=s.BoundBox
    bb=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    v=s.Volume-e['volume_mm3'];delta=max(abs(a-b)for a,b in zip(bb,e['bounds_xyz_mm']))
    assert s.isValid() and len(s.Solids)==e['solids'],n
    assert abs(v)<1e-4 and delta<1e-5,(n,v,delta)
    parts[n]={'valid':True,'solids':len(s.Solids),'volume_difference_mm3':v,'max_bound_difference_mm':delta}
clip=Part.makeBox(80,.1,80,App.Vector(-40,10,-40))
neck=Part.makeCompound([d.getObject(n).Shape.common(clip)for n in [args.shell_lower,args.shell_upper]])
pcb=d.getObject(args.pcb).Shape.common(clip);nb=neck.BoundBox;pb=pcb.BoundBox
assert max(abs(nb.XLength-15),abs(nb.ZLength-15),abs(pb.XLength-8),abs(pb.ZLength-1))<1e-5
assert abs(neck.Volume/.1-math.pi*(7.5**2-6**2))<1e-4
step=Part.Shape();step.read(str(p/args.step));assert step.isValid()
if r.get('combined_step_sha256'):assert sha(p/args.step)==r['combined_step_sha256']
if r.get('STEP_sha256'):assert sha(p/args.step)==r['STEP_sha256']
App.closeDocument(d.Name);assert sha(f)==before and sha(rp)==report_sha
out={'status':'PASS_saved_history_waist_and_STEP_only','native_sha256':before,'geometry_report_sha256':report_sha,
     'reviewer_sha256':sha(Path(__file__)),'method':'Independent saved-document reopen; touch every object and force full feature-history recompute without save. Compare final validity, solid count, volume and world bounds. Exact waist section and STEP read/hash check. No generator replay or independent motion/classification acceptance.',
     'parts':parts,'waist':{'outer_x_mm':nb.XLength,'outer_z_mm':nb.ZLength,'pcb_width_mm':pb.XLength,'pcb_thickness_mm':pb.ZLength,'pcb_metal_intersection_mm3':pcb.common(neck).Volume,'bare_board_clearance_mm':pcb.distToShape(neck)[0]},
     'STEP_valid':True,'STEP_solids':len(step.Solids),'source_reported_unintended_intersections':r.get('unintended_intersections'),
     'limit':'Nominal source consistency only. No continuous assembly, received parts, tolerances, actual fasteners, controls stroke, wire bends, sealing, strength, electrical behavior, comfort or wear acceptance.'}
(p/'root-independent-native-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in ['parts','source_reported_unintended_intersections']},indent=2))
