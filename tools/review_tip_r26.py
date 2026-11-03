"""Read-only forced native review and explicitly staged R26 assembly screens."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
nf=P/'StationaryTipR26.FCStd';rp=P/'geometry-report.json';r=read(rp);before=sha(nf);rh=sha(rp)
E=ROOT/'hardware/cad/tip-support-r26/candidate-e';R25=ROOT/'hardware/cad/motor-shell-mount-r25/candidate-d'
assert before==r['native_sha256']
assert sha(E/'StationaryTipR26.FCStd')==r['source_R26_native_sha256']
assert sha(E/'geometry-report.json')==r['source_R26_report_sha256']
assert sha(R25/'ShellMotorMountR25.FCStd')==r['source_R25_native_sha256']
assert sha(R25/'geometry-report.json')==r['source_R25_report_sha256']
planpath=ROOT/'hardware/design/tip-support-r26/wire-plan-c.json';plan=read(planpath)
curvaturepath=planpath.with_name('wire-plan-c-curvature.json');curvature=read(curvaturepath)
assert sha(planpath)==r['wire_plan_sha256']==r['wire_guide_plan_sha256']==curvature['plan_sha256']
for key in ['unexpected_intersections','nominal_mate_intersections','new_wire_unexpected_intersections','new_wire_nominal_mate_intersections','new_wire_conditional_flare_intersections']:assert not r[key],key
assert all(q['minimum_polynomial_radius_lower_bound_mm']>=2.5 and q['analytic_arc_radius_mm']==2.5 for q in curvature['rows'])
D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute();rows={}
def bounds(s):
 b=s.optimalBoundingBox(False,False)
 return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
for n,q in dict(r['parts'],**r['mates'],**r['allowances']).items():
 s=D.getObject(n).Shape;db=max(abs(a-b)for a,b in zip(bounds(s),q['bounds_xyz_mm']));dv=s.Volume-q['volume_mm3']
 assert s.isValid()and len(s.Solids)==q['solids']and db<1e-5 and abs(dv)<1e-4,(n,db,dv)
 rows[n]={'valid':True,'solids':len(s.Solids),'maximum_bounds_delta_mm':db,'volume_delta_mm3':dv}
external=[(o.Name,v.Name,v.Document.Name)for o in D.Objects for v in o.OutList if v.Document!=D];assert not external
def compare(a,b):
 exact=a.exportBrepToString()==b.exportBrepToString();removed,added=(0.,0.)if exact else(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume)
 assert abs(removed)<1e-4 and abs(added)<1e-4,(removed,added)
 return {'exact_BRep_equal':exact,'removed_mm3':removed,'added_mm3':added}
S=A.openDocument(str(E/'StationaryTipR26.FCStd'))
seed={n:compare(S.getObject(n).Shape,D.getObject(n).Shape)for n in r['preserved_source_R26_roles']}
A.closeDocument(S.Name)
S=A.openDocument(str(R25/'ShellMotorMountR25.FCStd'))
conserved={n:compare(S.getObject(n).Shape,D.getObject(n).Shape)for n in r['preserved_R25_roles']}
tip={}
for n in ['TipPCB','TipComponentEnvelope']:
 s=D.getObject(n).Shape.copy();s.translate(A.Vector(0,.77,0));tip[n]=compare(S.getObject(n).Shape,s)
A.closeDocument(S.Name)
wire_rows=[]
for q in plan['wires']:
 n=str(q['pin']);path=D.getObject('TipWirePathR26_'+n).Shape
 expected=edges_from_plan(q);assert len(path.Edges)==len(expected)
 edge_rows=[]
 for actual,planned,definition in zip(path.Edges,expected,q['curves']):
  # Re-read the saved spine, not just the swept solids or sampled planner.
  delta=max(actual.valueAt(actual.FirstParameter+(actual.LastParameter-actual.FirstParameter)*i/64).distanceToPoint(planned.valueAt(planned.FirstParameter+(planned.LastParameter-planned.FirstParameter)*i/64))for i in range(65))
  assert delta<1e-7
  if definition['kind']=='bezier5':
   poles=actual.Curve.getPoles();assert len(poles)==6
   dp=max(v.distanceToPoint(A.Vector(*p))for v,p in zip(poles,definition['poles_xyz_mm']));assert dp<1e-7
   edge_rows.append({'kind':'Bezier5','maximum_pole_delta_mm':dp,'maximum_parameter_sample_delta_mm':delta})
  else:
   assert abs(actual.Curve.Radius-2.5)<1e-8
   edge_rows.append({'kind':'circle','radius_mm':actual.Curve.Radius,'maximum_parameter_sample_delta_mm':delta})
 wire_rows.append({'pin':q['pin'],'native_insulated_path_length_mm':path.Length,'edges':edge_rows})
print(len(rows),'forced native roles; exact saved wire poles/circles and source conservation pass',flush=True)

def volume(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
parts={n:D.getObject(n).Shape for n in r['parts']};mates={n:D.getObject(n).Shape for n in r['mates']}
def pose(moving,fixed,y=0,angle=0):
 bad=[]
 for n,s0 in moving.items():
  s=s0.copy()
  if angle:s.rotate(A.Vector(),A.Vector(0,1,0),angle)
  if y:s.translate(A.Vector(0,y,0))
  for m,p in fixed.items():
   v=volume(s,p)
   if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
 return bad
old=read(ROOT/'hardware/cad/motor-retention-r21/candidate-c/geometry-report.json')
cartridge={n:parts.get(n,mates.get(n))for n in old['cartridge_roles']if n not in ['PortedCarrierR20','MotorKeeperR21','MotorMaxEnvelope','MotorLeadFlareAllowanceR21']}
cartridge.update({n:parts[n]for n in ['TipReadyCarrierR26','PCBOnlyKeeperR25']})
loading=[]
for y in range(100,-1,-5):
 hits=pose(cartridge,{'KeyedBodyR25':parts['KeyedBodyR25']},y);loading.append({'Y_offset_mm':y,'hits':hits})
print('electronics/body poses',[x for x in loading if x['hits']],flush=True)
tipnames=['StationaryTipCarrierR26','TipPCB','TipComponentEnvelope','StationaryPickupShoeR26','TipClipFittedEnvelopeR26','TipDielectricBondR26','TipCapThermalGelR26']
wire_names=[n for n in parts if n.startswith(('TipWireR26_','TipBareWireR26_','TipSolderAllowanceR26_'))]
motor_names=['ShellMotorMountR25','MotorClampScrewR25','MotorClampNutR25','MotorMaxEnvelope']
motor={n:parts[n]for n in motor_names};motor['MotorLeadFlareAllowanceR21']=D.getObject('MotorLeadFlareAllowanceR21').Shape
waiting=set(tipnames+wire_names+motor_names+['TipCarrierScrewEnvelopeR26','MotorSeatCapR25'])
fixed={n:s for n,s in dict(parts,**mates).items()if n not in waiting}
motorposes=[]
for y in [100,80,60,40,20,10,5,2,1,.5,.25,0]:
 hits=pose(motor,fixed,y);motorposes.append({'Y_offset_mm':y,'hits':hits})
print('motor/updated tray poses',[x for x in motorposes if x['hits']],flush=True)
capfixed={n:parts[n]for n in tipnames+wire_names+['TipCarrierScrewEnvelopeR26']};capfixed['TipStrainReliefProcessAllowanceR26']=D.getObject('TipStrainReliefProcessAllowanceR26').Shape
cap=[]
for y in [20,5,1,.25,0]:
 for angle in [0,90,180,270]:
  cap.append({'Y_offset_mm':y,'angle_deg':angle,'hits':pose({'MotorSeatCapR25':parts['MotorSeatCapR25']},capfixed,y,angle)})
print('cap/final tip and wires poses',[x for x in cap if x['hits']],flush=True)
tipfixed={n:s for n,s in dict(parts,**mates).items()if n not in set(tipnames+wire_names+['TipCarrierScrewEnvelopeR26','MotorSeatCapR25'])}
tip7=pose({n:parts[n]for n in tipnames},tipfixed,7)
print('tip supported at +7Y before solder',tip7,flush=True)
# Generic bounded solder-tool envelope, with cap/screw/cured relief waiting.
# It approaches from below and rearward, not through the PCB or component face.
stage={n:s.copy()for n,s in tipfixed.items()}
for n in tipnames:
 s=parts[n].copy();s.translate(A.Vector(0,7,0));stage[n]=s
tools=[];direction=A.Vector(0,-1,-1);direction.normalize()
for q in plan['wires']:
 x,y,z=q['J101_pad_center_xyz_mm'];start=A.Vector(x,y+7-.15,z-.30)
 sphere=Part.makeSphere(.15,start);cone=Part.makeCone(.15,1.5,12,start,direction);shaft=Part.makeCylinder(1.5,20,start+direction*12,direction)
 tool=sphere.fuse(cone).fuse(shaft);hits=[]
 for n,s in stage.items():
  v=volume(tool,s)
  if v>1e-5:hits.append({'fixed':n,'intersection_mm3':v})
 tools.append({'pin':q['pin'],'start_xyz_mm':[start.x,start.y,start.z],'tip_radius_mm':.15,'cone_length_mm':12,'shaft_radius_mm':1.5,'shaft_length_mm':20,'direction':[direction.x,direction.y,direction.z],'hits':hits})
print('generic solder-tool access',[x for x in tools if x['hits']],flush=True)
out={'native_sha256':before,'geometry_report_sha256':rh,'reviewer_sha256':sha(Path(__file__)),'native_wire_library_sha256':sha(Path(__file__).with_name('tip_wire_native_r26.py')),'wire_plan_sha256':sha(planpath),'curvature_report_sha256':sha(curvaturepath),'source_R25_native_sha256':r['source_R25_native_sha256'],'source_R26E_native_sha256':r['source_R26_native_sha256'],'saved_roles':rows,'external_document_links':external,'source_R26E_conservation':seed,'source_R25_conservation':conserved,'tip_inverse_0_77Y_conservation':tip,'saved_wire_path_comparison':wire_rows,'electronics_into_body_listed_poses':loading,'motor_module_with_new_tray_listed_poses':motorposes,'cap_to_final_tip_and_wires_listed_poses':cap,'tip_module_at_plus7Y_hits':tip7,'generic_solder_tools_at_plus7Y':tools,'scope':'Forced saved native role validity/conservation and exact stored Bezier poles/circle radii. Finite rigid stage positions only: tip and wire ends wait during motor loading, free tails must be fed through ring before seating. No connected-harness loading/service-motion proof. Generic bounded solder tool at+7Y, no actual tip/wetting/hand or clip installation qualification. Source static screens and guards remain nominal allowances. BatteryOPEN.'}
all_motion=loading+motorposes+cap+tools;out['all_new_listed_screens_clear']=not tip7 and not any(x['hits']for x in all_motion)
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name);assert sha(nf)==before and sha(rp)==rh
assert out['all_new_listed_screens_clear'],'See saved-review.json for failed stage or tool; do not claim acceptance.'
print('saved R26 review; all new listed screens clear',flush=True)
