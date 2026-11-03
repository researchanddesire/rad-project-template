"""Fresh forced native R27 review; source conservation and assembly/tool screens."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/tip-support-r26/candidate-f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
rp=P/'geometry-report.json';r=read(rp);nf=P/'FlangeCradleR27.FCStd';before=sha(nf);rh=sha(rp)
assert before==r['native_sha256']and sha(SRC/'StationaryTipR26.FCStd')==r['source_native_sha256']
assert not r['unexpected_intersections']and not r['nominal_mate_intersections']
assert not any(q['hits']for q in r['island_listed_loading_poses'])
source_plug_failures=[q for q in r['nominal_mate_listed_approach_poses']if q['hits']]
D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute()
def bounds(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
rows={}
for n,q in dict(r['parts'],**r['mates'],**r['allowances']).items():
 s=D.getObject(n).Shape;delta=max(abs(a-b)for a,b in zip(bounds(s),q['bounds_xyz_mm']));dv=s.Volume-q['volume_mm3']
 assert s.isValid()and len(s.Solids)==q['solids']and delta<1e-5 and abs(dv)<1e-4,(n,delta,dv)
 rows[n]={'valid':True,'solids':len(s.Solids),'maximum_bounds_delta_mm':delta,'volume_delta_mm3':dv}
external=[(o.Name,v.Name)for o in D.Objects for v in o.OutList if v.Document!=D];assert not external
q=r['chosen_rotation'];c=A.Vector(*q['center_xyz_mm']);t=A.Placement(c+A.Vector(*q['translation_xyz_mm']),A.Rotation(A.Vector(*q['axis']),q['angle_deg'])).multiply(A.Placement(-c,A.Rotation()))
S=A.openDocument(str(SRC/'StationaryTipR26.FCStd'));conserved={};rotated={}
for n in list(r['preserved_roles'])+list(r['inverse_transformed_flange_roles']):
 s=S.getObject(n).Shape;now=D.getObject(n).Shape.copy();rot=n in r['inverse_transformed_flange_roles']
 if rot:now.Placement=t.inverse().multiply(now.Placement)
 if rot:
  for ref,c0 in r.get('local_header_half_turns',{}).items():
   if n in ['R17_'+ref,'R17Mate_'+ref]:
    c0=A.Vector(*c0);half=A.Placement(c0,A.Rotation(A.Vector(0,0,1),180)).multiply(A.Placement(-c0,A.Rotation()));now.Placement=half.inverse().multiply(now.Placement)
 exact=s.exportBrepToString()==now.exportBrepToString();a,b=(0,0)if exact else(s.copy().cut(now.copy()).Volume,now.copy().cut(s.copy()).Volume)
 assert abs(a)<1e-4 and abs(b)<1e-4,(n,a,b)
 (rotated if rot else conserved)[n]={'exact_BRep_equal':exact,'removed_mm3':a,'added_mm3':b}
hub_removed=S.getObject('HubLeft').Shape.copy().cut(D.getObject('FlangeSupportHubR27').Shape.copy()).Volume;assert abs(hub_removed)<1e-4
A.closeDocument(S.Name)
def volume(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
parts={n:D.getObject(n).Shape for n in r['parts']};mates={n:D.getObject(n).Shape for n in r['mates']}
flange=set(r['inverse_transformed_flange_roles']);covers={'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference'}
hub='FlangeSupportHubR27';keeper='FlangeEndKeeperR27';screw='FlangeKeeperScrewEnvelopeR27'
def shift_hits(moving,fixed,offset):
 hits=[]
 for n,original in moving.items():
  s=original.copy();s.translate(A.Vector(*offset))
  for m,p in fixed.items():
   v=volume(s,p)
   if v>1e-5:hits.append({'moving':n,'fixed':m,'intersection_mm3':v})
 return hits
# Fit left hub/cradle before the flange island, all plugs/covers/bolts waiting.
waiting=flange|covers|{hub,keeper,screw,'HubBolt_1','HubBolt1','HubNut_1','HubNut1'}
fixed={n:s for n,s in dict(parts,**mates).items()if n not in waiting};hubposes=[]
for x in [-30,-20,-10,-5,-2,-1,-.5,-.25,0]:
 hubposes.append({'X_offset_mm':x,'hits':shift_hits({hub:parts[hub]},fixed,[x,0,0])})
print('new hub side-loading',[q for q in hubposes if q['hits']],flush=True)
# Keeper and screw enter from rear before elastomer/service covers.
fixed={n:s for n,s in dict(parts,**mates).items()if n not in covers|{keeper,screw}};kp=[]
for y in [-20,-10,-5,-2,-1,-.5,-.25,0]:kp.append({'Y_offset_mm':y,'hits':shift_hits({keeper:parts[keeper]},fixed,[0,y,0])})
print('keeper approach',[q for q in kp if q['hits']],flush=True)
fixed[keeper]=parts[keeper];sp=[]
for y in [-20,-10,-5,-2,-1,-.5,-.25,0]:
 hits=shift_hits({screw:parts[screw]},fixed,[0,y,0]);named=[h for h in hits if h['fixed']==hub]
 unexpected=[h for h in hits if h['fixed']!=hub]
 sp.append({'Y_offset_mm':y,'hits':unexpected,'named_screw_pilot_intersections':named})
print('screw approach',[q for q in sp if q['hits']],flush=True)
tool=Part.makeCylinder(1.1,24,A.Vector(r.get('keeper_boss_X_mm',-32.5),-45.4,9.1),A.Vector(0,1,0));toolhits=[]
for n,s in fixed.items():
 v=volume(tool,s)
 if v>1e-5:toolhits.append({'fixed':n,'intersection_mm3':v})
print('generic 2.2mm tool shaft',toolhits,flush=True)
# Access directions are a location report only: rear cover is still solid.
controls=[]
for ref in ['SW1','SW2']:
 s=parts['R17_'+ref];bb=s.optimalBoundingBox(False,False)
 controls.append({'ref':ref,'envelope_center_XZ_mm':[(bb.XMin+bb.XMax)/2,(bb.ZMin+bb.ZMax)/2],'maximum_actuator_envelope_front_Y_mm':bb.YMin,'press_direction_xyz':[0,1,0],'scope':'Shorter rear-facing linkage opportunity; no window, membrane, return or accepted operating stroke yet.'})
out={'native_sha256':before,'geometry_report_sha256':rh,'source_R26_native_sha256':r['source_native_sha256'],'reviewer_sha256':sha(Path(__file__)),'saved_roles':rows,'external_document_links':external,'preserved_source_roles':conserved,'inverse_transformed_flange_roles':rotated,'source_hub_material_removed_mm3':hub_removed,'hub_listed_side_loading_poses':hubposes,'keeper_listed_approach_poses':kp,'screw_listed_approach_poses':sp,'generic_2_2mm_tool_shaft_hits':toolhits,'control_access_locations':controls,'scope':'Forced saved geometry and source/inverse-pose conservation. Finite stage screens with actual plugs/covers explicitly waiting; screw/pilot is named unqualified process interface. Generic tool shaft only, not real driver/head/thread proof. Rear-facing switches remain behind unchanged solid cover; no enabled controls, flex/wiring, load/compliance, sealing, RF or physical acceptance.'}
out['source_nominal_mate_approach_failures']=source_plug_failures
if r.get('local_header_half_turns'):
 pp=ROOT/'hardware/pcb/flange-access-r28/candidate-a';pr=read(pp/'placement-inspection.json')
 assert sha(pp/'flange-r28.kicad_pcb')==r['placement_R28_native_sha256']==pr['native_board_sha256']
 assert sha(pp/'placement-inspection.json')==r['placement_R28_inspection_sha256']
 boxes=[]
 for p in pr['placements']:
  a,b,c,d=p['body_xy_mm'];lo,hi=p['z_bounds_mm'];pts=[t.multVec(A.Vector(x,y,z))for x in [a,c]for y in [b,d]for z in [lo,hi]]
  wanted=[min(getattr(v,k)for v in pts)for k in ['x','y','z']]+[max(getattr(v,k)for v in pts)for k in ['x','y','z']]
  delta=max(abs(x-y)for x,y in zip(bounds(parts['R17_'+p['ref']]),wanted));assert delta<1e-5,(p['ref'],delta)
  boxes.append({'ref':p['ref'],'maximum_Fab_height_box_bounds_delta_mm':delta})
 out['native_R28_placement_geometry_binding']={'native_board_sha256':pr['native_board_sha256'],'inspection_sha256':sha(pp/'placement-inspection.json'),'all_24_Fab_height_boxes':boxes,'electrical_status':'Pose correction only; source copper needs repair/native DRC. No electrical build acceptance.'}
out['new_hub_keeper_tool_screens_clear']=not toolhits and not any(q['hits']for q in hubposes+kp+sp)
out['all_new_listed_screens_clear']=out['new_hub_keeper_tool_screens_clear']and not source_plug_failures
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name)
assert sha(nf)==before and sha(rp)==rh
print(len(rows),'forced saved roles; new hub/keeper/tools clear',out['new_hub_keeper_tool_screens_clear'],'all stages clear',out['all_new_listed_screens_clear'],'source plug failures',len(source_plug_failures),flush=True)
