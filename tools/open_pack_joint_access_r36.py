"""Open the return-joint pocket for staged soldering; check finite generic probes."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/cad/pack-sensor-r36/connected-h';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((SOURCE/'geometry-report.json').read_text());v=json.loads((SOURCE/'saved-review.json').read_text());source=SOURCE/'ConnectedPackSensorsR36.FCStd';before=sha(source);assert before==r['native_sha256']==v['native_sha256']and r['all_static_screens_clear']and v['all_reviewed_screens_clear'];D=A.openDocument(str(source))
tool=D.addObject('Part::Box','ReturnJointServiceColumnR36');tool.Length=4.;tool.Width=3.4;tool.Height=22.15;tool.Placement.Base=A.Vector(9.8,-15.33,-2.95)
old=D.getObject('ConnectedSensorWiredRightHubR36');right=D.addObject('Part::Cut','ServiceablePackHubR36');right.Base=old;right.Tool=tool;right.Refine=True;D.recompute();assert right.Shape.isValid()and len(right.Shape.Solids)==1
loss=old.Shape.copy().cut(right.Shape.copy());outside=0. if loss.isNull()else loss.copy().cut(tool.Shape.copy()).Volume;assert outside<1e-5
# Preserve the complete existing upper-nut bearing region through X9.6.
witness=old.Shape.copy().common(Part.makeBox(4.,6.,7.,A.Vector(5.6,-14.,4.5)))
witness_loss=witness.copy().cut(right.Shape.copy()).Volume;assert witness_loss<1e-5
def feature(n,s):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;return o
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
physical={n:D.getObject(n).Shape.copy()for n in r['fixed_roles']+r['new_roles']if n!='ConnectedSensorWiredRightHubR36'};physical[right.Name]=right.Shape.copy()
waiting=['FlangeCoverLower','FlangeCoverUpper','ButtonServiceCoverR31']
fixed={n:s for n,s in physical.items()if n not in waiting}
probes=[]
for name,origin,axis,target in [('ReturnJoint',A.Vector(11.3,-13.63,-1.85),A.Vector(0,0,1),'SensorReturnYJointR36')]+[
 ('Lap'+row['pair'],A.Vector(19.8,-14.43,next(q['coated_end_xyz_mm'][2]for q in json.loads((ROOT/'hardware/cad/pack-sensor-r36/candidate-c/geometry-report.json').read_text())['factory_lead_plan']if q['sensor']=='TH'+row['pair'][0]and str(q['pair_lead'])==row['pair'][2])),A.Vector(0,1,0),'NTCSpliceSpaceR36_'+row['pair'])for row in r['joint_construction']]:
 # Generic last8mm D1.2 + next14mm D3.0. These dimensions do not claim an
 # actual iron, holder, hand access or solder quality has been accepted.
 tip=Part.makeCylinder(.6,8.,origin,axis);shaft=Part.makeCylinder(1.5,14.,origin+axis*8.,axis);shape=tip.fuse(shaft).removeSplitter();assert shape.isValid()and len(shape.Solids)==1
 feature('SolderAccessProbeR36_'+name,shape)
 poses=[]
 for offset in [0,2,5,10,20]:
  moving=shape.copy();moving.translate(axis*offset);hits=[]
  for n,s in fixed.items():
   common=moving.copy().common(s.copy())if vol(moving,s)>1e-5 else None
   if common is None:continue
   # Contact at the target joint is intentional. All geometry outside that
   # process volume, including neighboring wires, must clear.
   remaining=common.copy().cut(physical[target].copy()).Volume
   if remaining>1e-5:hits.append({'fixed':n,'intersection_outside_target_mm3':remaining})
  poses.append({'approach_offset_mm':offset,'unexpected_hits':hits})
 probes.append({'name':name,'origin_xyz_mm':list(origin),'axis_xyz':list(axis),'target_process_role':target,'generic_profile_mm':{'tip_diameter':1.2,'tip_length':8.,'shaft_diameter':3.,'shaft_length':14.},'poses':poses})
 print('probe',name,poses,flush=True)
gaps={n:feature('NominalProbeGapR36_'+n,Part.makeVertex(A.Vector())).Name for n in []}
return_probe=D.getObject('SolderAccessProbeR36_ReturnJoint').Shape
for n in ['HubBolt1','HubNut1','KeyedBodyR25']:
 gaps[n]=return_probe.distToShape(physical[n])[0]
out=OUT/'ServiceablePackSensorsR36.FCStd';D.Label='R36 joint service opening and generic finite tool probes / DEVELOPMENT';D.saveAs(str(out));result={'native_sha256':sha(out),'source_connected_H_sha256':before,'source_review_sha256':sha(SOURCE/'saved-review.json'),'builder_sha256':sha(Path(__file__)),'service_column_xyz_mm':[9.8,-15.33,-2.95,13.8,-11.93,19.2],'source_hub_removed_mm3':loss.Volume,'removed_outside_column_mm3':outside,'upper_nut_bearing_witness_loss_mm3':witness_loss,'right_hub_solids':len(right.Shape.Solids),'waiting_covers':waiting,'generic_tool_probes':probes,'nominal_return_probe_gap_mm':gaps,'all_listed_tool_poses_clear':all(not p['unexpected_hits']for q in probes for p in q['poses']),'scope':'New front-of-pack service column opens upward with covers waiting, while source wire poses and target joints remain. Generic tool finite samples and one nut-seat material witness only; actual iron/tip/holder/hand access, continuous motion, restraint, hub strength, solder and physical acceptance remain unqualified. Power mate and connected full assembly remain unfinished; batteryOPEN/BOMunchanged.'};(OUT/'access-review.json').write_text(json.dumps(result,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('SAVED service access clear',result['all_listed_tool_poses_clear'],'gaps',gaps,flush=True)
