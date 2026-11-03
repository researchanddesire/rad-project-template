"""Fresh forced saved-history and independent motor load-path geometry review."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
P=Path(sys.argv[1]).resolve();src=Path(sys.argv[2]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rp=P/'geometry-report.json';r=json.loads(rp.read_text());nf=P/'ShellMotorMountR25.FCStd';before=sha(nf);rh=sha(rp)
assert before==r['native_sha256']and sha(src)==r['source_native_sha256']
assert not r['unexpected_intersections']and not r['nominal_mate_intersections']and not r['conditional_flare_intersections']
for key in ['motor_module_listed_loading_poses','cap_to_motor_tip_listed_poses','motor_into_clamp_listed_poses','board_drop_listed_poses','PCB_keeper_drop_listed_poses']:
 assert not any(v['hits']for v in r[key]),key
D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute();rows={}
def inv(s):
 b=s.optimalBoundingBox(False,False)
 return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
for n,q in dict(r['parts'],**r['mates'],**r['allowances']).items():
 s=D.getObject(n).Shape
 delta=max(abs(a-b)for a,b in zip(inv(s),q['bounds_xyz_mm']));dv=s.Volume-q['volume_mm3']
 assert s.isValid()and len(s.Solids)==q['solids']and delta<1e-5 and abs(dv)<1e-4,(n,delta,dv)
 rows[n]={'valid':True,'solids':len(s.Solids),'maximum_bounds_delta_mm':delta,'volume_delta_mm3':dv}
external=[(o.Name,v.Name,v.Document.Name)for o in D.Objects for v in o.OutList if v.Document!=D]
assert not external
source=A.openDocument(str(src));conserved={}
for n in r['preserved_roles']:
 a=source.getObject(n).Shape.copy();b=D.getObject(n).Shape.copy();exact=a.exportBrepToString()==b.exportBrepToString()
 removed,added=(0,0)if exact else(a.cut(b).Volume,b.cut(a).Volume)
 assert removed<1e-4 and added<1e-4,(n,removed,added)
 conserved[n]={'removed_mm3':removed,'added_mm3':added,'exact_BRep_equal':exact}
subsets={}
for n,old in [('PortedCarrierR20','PortedCarrierR20'),('PCBOnlyKeeperR25','MotorKeeperR21'),('KeyedBodyR25','KeyedOnePieceBody')]:
 a=source.getObject(old).Shape.copy();b=D.getObject(n).Shape.copy();added=b.cut(a).Volume
 assert added<1e-4,(n,added)
 subsets[n]={'added_outside_source_mm3':added,'removed_mm3':a.cut(b).Volume}
oldcap=source.getObject('FullerClosingCap').Shape.copy();newcap=D.getObject('MotorSeatCapR25').Shape.copy()
reference_cap=newcap.copy()
if 'cap_assembly'in r:
 q=r['cap_assembly'];assembly=A.Placement(A.Vector(0,q['Y_translation_mm'],0),A.Rotation(A.Vector(0,1,0),q['Y_rotation_deg']));reference_cap.Placement=assembly.inverse().multiply(reference_cap.Placement)
assert oldcap.cut(reference_cap).Volume<1e-4
cap_added=reference_cap.cut(oldcap)
outside_shoulder=cap_added.cut(D.getObject('CapClampShoulderR25').Shape.copy()).Volume
assert outside_shoulder<1e-4
# Direct contacts to the electronics support would undermine the architecture.
motor=D.getObject('ShellMotorMountR25').Shape
gaps={n:motor.distToShape(D.getObject(n).Shape)[0]for n in ['PortedCarrierR20','PCBOnlyKeeperR25','BodyPCB_R17','NarrowPackAllowance']}
assert all(v>=.5 for v in gaps.values()),gaps
assert not(set(r['removed_motor_support_features'])&{o.Name for o in D.getObject('ConnectedCarrierBlank').Shapes})
# Native owner-side sections, keeping the actual beam and half the clamp.
cut=Part.makeBox(100,250,100,A.Vector(-100,-100,-50));meshes={}
for n in ['KeyedBodyR25','MotorSeatCapR25','ShellMotorMountR25']:
 s=D.getObject(n).Shape.copy().common(cut.copy());assert s.isValid()and s.Volume>0
 p=P/(n+'-side-section.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.12,Relative=False).write(str(p));meshes[p.name]=sha(p)
out={'native_sha256':before,'geometry_report_sha256':rh,'source_native_sha256':sha(src),'reviewer_sha256':sha(Path(__file__)),'saved_roles':rows,'preserved_source_roles':conserved,'source_subset_checks':subsets,'cap_added_volume_mm3':cap_added.Volume,'cap_added_outside_declared_internal_shoulder_mm3':outside_shoulder,'motor_mount_clearances_mm':gaps,'external_document_links':external,'side_section_meshes_sha256':meshes,'scope':'Fresh forced saved native validity/bounds/material conservation; motor supports removed from electronics graph; independent separated mount and nominal source-bound geometry. Finite builder pose results bound by report hash, not continuous motion or actual flexible wires. No material, clamp preload/stress, body/cap stop priority, actual contact, vibration transmission, seal or physical qualification.'}
A.closeDocument(source.Name);A.closeDocument(D.Name)
assert sha(nf)==before and sha(rp)==rh
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(rows),'saved roles; source subsets; internal cap addition; gaps',gaps,flush=True)
