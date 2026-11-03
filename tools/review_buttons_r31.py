"""Fresh saved R31 geometry and finite rigid button/assembly screens.

Silicone deformation, actual switch stroke/force and threads are not modeled.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();PLAN=Path(sys.argv[2]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r=read(P/'geometry-report.json');nf=P/'ButtonsR31.FCStd';before=sha(nf);assert before==r['native_sha256']and not r['unexpected_intersections'];plan=read(PLAN);guard=read(PLAN.with_name('plan-review.json'));assert sha(PLAN)==r['updated_wire_plan_sha256']==guard['reviewed_plan_sha256']and guard['all_curves_R_at_least_4mm_and_separated']
D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute()
def bb(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
roles={};shapes={}
for n,q in dict(r['parts'],**r['mates'],**r['allowances']).items():
 s=D.getObject(n).Shape;dv=s.Volume-q['volume_mm3'];delta=max(abs(a-b)for a,b in zip(bb(s),q['bounds_xyz_mm']));assert s.isValid()and len(s.Solids)==q['solids']and abs(dv)<1e-4 and delta<1e-5,(n,dv,delta);roles[n]={'valid':True,'solids':len(s.Solids),'volume_delta_mm3':dv,'maximum_bounds_delta_mm':delta};shapes[n]=s
external=[(o.Name,x.Name)for o in D.Objects for x in o.OutList if x.Document!=D];assert not external
S=A.openDocument(str(ROOT/'hardware/cad/harness-support-r30/candidate-b/HarnessSupportR30.FCStd'));conserved={}
for n in r['source_roles_conserved']:
 a=S.getObject(n).Shape;b=shapes[n];eq=a.exportBrepToString()==b.exportBrepToString();remove,add=(0.,0.)if eq else(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume);delta=max(abs(x-y)for x,y in zip(bb(a),bb(b)));assert abs(remove)<1e-4 and abs(add)<1e-4 and delta<1e-5,(n,remove,add,delta);conserved[n]={'exact_BRep_equal':eq,'removed_mm3':remove,'added_mm3':add,'maximum_bounds_delta_mm':delta}
material={}
for old,new in r['replaced_roles'].items():
 a=S.getObject(old).Shape;b=shapes[new];removed=a.copy().cut(b.copy());allowed=D.getObject('ButtonCoverCutToolsR31').Shape if old=='ServiceCoverReference'else D.getObject('ButtonUpperExitReliefR31').Shape if old=='HarnessKeeperR30'else Part.Shape();residual=removed.Volume if allowed.isNull()else removed.copy().cut(allowed.copy()).Volume;assert abs(residual)<1e-4,(old,residual);material[old]={'replacement':new,'removed_mm3':removed.Volume,'added_mm3':b.copy().cut(a.copy()).Volume,'outside_declared_removal_mm3':residual}
 # The R30 screw boss and its supporting lower keeper remain untouched.
 if old=='HarnessKeeperR30':
  witness=a.copy().common(Part.makeBox(100,100,108.6,A.Vector(-50,-60,-100)));lost=witness.copy().cut(b.copy()).Volume;assert witness.Volume>1 and abs(lost)<1e-5;material[old]['all_source_material_below_Z8_6_lost_mm3']=lost
A.closeDocument(S.Name)
paths=[]
for q in plan['wires']:
 edges=D.getObject('InterboardPathR29_'+str(q['pin'])).Shape.Edges;wanted=edges_from_plan(q);assert len(edges)==len(wanted);errors=[]
 for i,(a,b)in enumerate(zip(edges,wanted)):
  assert abs(a.Length-b.Length)<1e-6
  if q['curves'][i]['kind']=='bezier5':
   aa,bc=a.Curve.getPoles(),b.Curve.getPoles();assert len(aa)==len(bc)==6;err=max((u-v).Length for u,v in zip(aa,bc))
  else:err=max(abs(a.Curve.Radius-b.Curve.Radius),(a.Curve.Center-b.Curve.Center).Length)
  assert err<1e-7;errors.append(err)
 paths.append({'pin':q['pin'],'stored_curve_errors_mm':errors,'native_path_length_mm':sum(e.Length for e in edges)})
named={tuple(sorted([q['a'],q['b']]))for q in r['named_unqualified_pin_pilot_interfaces']};seen=set();hits=[];interfaces=[];pairs=0
for n in r['new_roles']:
 for m,b in shapes.items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(shapes[n],b)
  if v>1e-5:(interfaces if key in named else hits).append({'a':n,'b':m,'intersection_mm3':v})
 print('fresh static',n,flush=True)
meshes={}
for n in r['new_roles']+['FlangePCB_R17','R17_SW1','R17_SW2','R17Mate_J7']:
 f=P/(n+'.stl');MeshPart.meshFromShape(Shape=shapes[n],LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
# Real Boolean section faces for the single-button review figure. This
# section excludes the left side of SW2 and crops the remote cover.
sectionbox=Part.makeBox(2.15,12.2,10,A.Vector(-15.35,-30.1,.5));sectionmeshes={}
for n in ['ButtonServiceCoverR31','ButtonBezelR31','ButtonBootR31','ButtonPlungerR31_SW2','ButtonHomePinR31_SW2','ButtonStopScrewR31_SW2','R17_SW2','FlangePCB_R17']:
 s=shapes[n].copy().common(sectionbox.copy())
 if s.Volume<=1e-7:continue
 f=P/(n+'-section.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.025,AngularDeflection=.1,Relative=False).write(str(f));sectionmeshes[f.name]=sha(f)
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'reviewer_sha256':sha(Path(__file__)),'source_R30_native_sha256':r['source_R30_native_sha256'],'wire_plan_sha256':sha(PLAN),'wire_plan_guard_sha256':sha(PLAN.with_name('plan-review.json')),'path_library_sha256':sha(Path(__file__).with_name('tip_wire_native_r26.py')),'saved_roles':roles,'source_roles_conserved':conserved,'changed_material':material,'external_document_links':external,'stored_wire_curves':paths,'forced_new_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_pin_pilot_interfaces':interfaces,'meshes_sha256':meshes,'scope':'Fresh forced saved rest geometry and source conservation. New wire paths and modified capture pad recomputed; exact stored poles/circles compared. Pin press-fit and screw/pilot overlaps are named unqualified process interfaces. Silicone return/seal, switch overtravel/force/life, tapping/preload/strength and physical fit remain unproven.'}
out['section_meshes_sha256']=sectionmeshes;out['section_crop_bounds_xyz_mm']=[-15.35,-30.1,.5,-13.2,-17.9,10.5]
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');assert not hits,hits
# Rigid .58mm study motion. The own-switch Fab/height box is reported as
# intentional encounter, not interpreted as actual actuator compression.
press=[];study=.58
for ref in ['SW1','SW2']:
 moving=['ButtonPlungerR31_'+ref,'ButtonHomePinR31_'+ref];omitted={'ButtonBootR31'}|set(moving);own='R17_'+ref
 for y in [0,.1,.2,.3,.4,.5,study]:
  bad=[];intended=[]
  for n in moving:
   s=shapes[n].copy();s.translate(A.Vector(0,y,0))
   for m,b in shapes.items():
    if m in omitted:continue
    v=vol(s,b)
    if v>1e-5:(intended if m==own else bad).append({'moving':n,'fixed':m,'intersection_mm3':v})
  s=shapes[moving[0]].copy();s.translate(A.Vector(0,y,0));distance=s.distToShape(shapes['ButtonStopScrewR31_'+ref])[0];press.append({'switch':ref,'study_Y_travel_mm':y,'unexpected_hits':bad,'own_switch_conservative_box_encounters':intended,'distance_to_adjustable_stop_mm':distance})
  print('press',ref,y,bad,'stopgap',distance,flush=True)
def stage(moving,fixed,offsets,axis):
 rows=[]
 for value in offsets:
  delta=[0.,0.,0.];delta[axis]=value;bad=[]
  for n in moving:
   s=shapes[n].copy();s.translate(A.Vector(*delta))
   for m,b in fixed.items():
    if tuple(sorted([n,m]))in named:continue
    v=vol(s,b)
    if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
  rows.append({'offset_xyz_mm':delta,'hits':bad});print('stage',moving[0],delta,bad,flush=True)
 return rows
module={n for n in shapes if n.startswith('Button')and n not in ['ButtonKeeperR31','ButtonSupportHubR31']};covers={'FlangeCoverLower','FlangeCoverUpper'};stages={}
stages['complete_cover_module_from_rear']=stage(sorted(module),{n:s for n,s in shapes.items()if n not in module|covers},[-15,-10,-5,-2,-1,-.5,-.2,0],1)
stages['keeper_with_formed_wires_and_cover_waiting']=stage(['ButtonKeeperR31'],{n:s for n,s in shapes.items()if n not in module|covers|{'ButtonKeeperR31','FlangeKeeperScrewEnvelopeR27'}},[-20,-10,-5,-2,-1,-.5,-.1,0],1)
# Calibration tool is only a straight shaft/hex-key access allowance, not a
# supplier drive profile. Boot/bezel wait while setting the stops.
tools=[]
for q in r['button_spec']:
 x,z=q['center_XZ_mm'];probe=Part.makeCylinder(.65,14,A.Vector(x,-42,8),A.Vector(0,1,0));bad=[]
 for n,b in shapes.items():
  if n in {'ButtonBootR31','ButtonBezelR31'}:continue
  v=vol(probe,b)
  if v>1e-5:bad.append({'fixed':n,'intersection_mm3':v})
 tools.append({'switch':q['switch'],'shaft_diameter_mm':1.3,'unexpected_hits':bad})
# The loose-end R30 stage remains usable only for the unchanged body prefix;
# rescreen changed left hub and populated-board slide against its actual tails.
park=ROOT/'hardware/cad/harness-support-r30/parked-d';pr=read(park/'parking-review.json');assert sha(park/'ParkedHarnessR30.FCStd')==pr['native_sha256'];S=A.openDocument(str(park/'ParkedHarnessR30.FCStd'));tails={q['role']:S.getObject(q['role']).Shape.copy()for q in pr['wires']}
for q in plan['wires']:
 actual=S.getObject('ParkedPathR30_'+str(q['pin'])).Shape.Edges[:2];expected=edges_from_plan({'curves':q['curves'][:2]});assert all(max((x-y).Length for x,y in zip(a.Curve.getPoles(),b.Curve.getPoles()))<1e-7 for a,b in zip(actual,expected))
A.closeDocument(S.Name);r27=read(ROOT/'hardware/cad/flange-controls-r27/candidate-d/geometry-report.json');island=set(r27['inverse_transformed_flange_roles']);hardware={'HubBolt_1','HubBolt1','HubNut_1','HubNut1','FlangeKeeperScrewEnvelopeR27'};oldwires={n for n in shapes if n.startswith('InterboardWireR29_')};absent=module|covers|hardware|{'ButtonKeeperR31','FlangeAnchorPadR30'}|oldwires
fixed={n:s for n,s in shapes.items()if n not in absent|island|{'ButtonSupportHubR31'}};fixed.update(tails);stages['left_hub_with_loose_flange_ends']=stage(['ButtonSupportHubR31'],fixed,[-30,-20,-10,-5,-2,-1,-.5,-.25,0],0)
board=sorted(n for n in island if n in r['parts']);fixed={n:s for n,s in shapes.items()if n not in absent|set(board)|{n for n in r['mates']if n in island}};fixed.update(tails);stages['populated_flange_with_loose_ends']=stage(board,fixed,[-50,-40,-30,-20,-10,-5,-2,-1,-.5,-.25,0],0)
allclear=not any(q['unexpected_hits']for q in press+tools)and not any(q['hits']for rows in stages.values()for q in rows)
screen={'native_sha256':before,'saved_review_sha256':sha(P/'saved-review.json'),'screener_sha256':sha(Path(__file__)),'source_parked_native_sha256':pr['native_sha256'],'source_parked_report_sha256':sha(park/'parking-review.json'),'source_prefixes_equal':True,'rigid_press_study':press,'assembly_stages':stages,'calibration_tool_shafts':tools,'all_listed_screens_clear':allclear,'scope':'Finite rigid poses only. Complete rear cover module has the two flange skins waiting. Press study omits deforming silicone, reports own-switch conservative envelope as intentional and leaves actual contact/overtravel unknown. Does not prove continuous paths, actual wire forming, hands/tool engagement, boots/gasket deformation/return/seal or switch force/life.'};(P/'assembly-screen.json').write_text(json.dumps(screen,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('fresh roles',len(roles),'conserved',len(conserved),'staticpairs',pairs,'stages clear',allclear,flush=True)
