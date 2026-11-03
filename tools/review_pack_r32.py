"""Fresh saved pack geometry, source material and finite assembly screens.

No actual pack selected, deformation, forces, thermal contact or wire routing
acceptance is inferred. Contact-film boxes are process reservations only.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/buttons-r31/candidate-d';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'geometry-report.json');nf=P/'PackRetentionR32.FCStd';before=sha(nf);assert before==r['native_sha256']and not r['unexpected_intersections']and not r['unexpected_rigid_vs_module_reservation_intersections'];D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute()
def bb(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
physical={};roles={};reservations={}
for n,q in dict(r['parts'],**r['mates'],**r['allowances'],**r['co_moving_size_reservations']).items():
 s=D.getObject(n).Shape;dv=s.Volume-q['volume_mm3'];delta=max(abs(a-b)for a,b in zip(bb(s),q['bounds_xyz_mm']));assert s.isValid()and len(s.Solids)==q['solids']and abs(dv)<1e-4 and delta<1e-5,(n,dv,delta);roles[n]={'valid':True,'solids':len(s.Solids),'volume_delta_mm3':dv,'maximum_bounds_delta_mm':delta};(reservations if n in r['co_moving_size_reservations']else physical)[n]=s
external=[(o.Name,x.Name)for o in D.Objects for x in o.OutList if x.Document!=D];assert not external
S=A.openDocument(str(SRC/'ButtonsR31.FCStd'));assert sha(SRC/'ButtonsR31.FCStd')==r['source_R31_native_sha256'];conserved={}
for n in r['source_roles_conserved']:
 a=S.getObject(n).Shape;b=D.getObject(n).Shape;eq=a.exportBrepToString()==b.exportBrepToString();remove,add=(0.,0.)if eq else(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume);delta=max(abs(x-y)for x,y in zip(bb(a),bb(b)));assert abs(remove)<1e-4 and abs(add)<1e-4 and delta<1e-5,(n,remove,add,delta);conserved[n]={'exact_BRep_equal':eq,'removed_mm3':remove,'added_mm3':add,'maximum_bounds_delta_mm':delta}
old=S.getObject('TipReadyCarrierR26').Shape;new=physical['PackRetainingCarrierR32'];removed=old.copy().cut(new.copy());tools=D.getObject('PackSensorWindowToolsR32').Shape;outside=removed.copy().cut(tools.copy()).Volume;assert abs(outside)<1e-4;protected={}
for n in ['TipReceiverR26','SupportedWireCombR26']:
 a=S.getObject(n).Shape;lost=a.copy().cut(new.copy()).Volume;assert a.Volume>1 and abs(lost)<1e-5;protected[n]={'source_witness_volume_mm3':a.Volume,'lost_mm3':lost}
for label,region in [('body_capture_rear_Y_below26',Part.makeBox(100,66,100,A.Vector(-50,-40,-50))),('PCB_guides_Z_above_minus1_2',Part.makeBox(100,100,51.2,A.Vector(-50,-20,-1.2)))]:
 witness=old.copy().common(region);lost=witness.copy().cut(new.copy()).Volume;assert witness.Volume>1 and abs(lost)<1e-5;protected[label]={'source_witness_volume_mm3':witness.Volume,'lost_mm3':lost}
A.closeDocument(S.Name);named={tuple(sorted([q['a'],q['b']]))for q in r['named_unqualified_screw_pilot_interfaces']};seen=set();hits=[];interfaces=[];pairs=0
for n in r['new_roles']:
 for m,b in physical.items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(physical[n],b)
  if v>1e-5:(interfaces if key in named else hits).append({'a':n,'b':m,'intersection_mm3':v})
 print('fresh static',n,flush=True)
module={n:s for n,s in physical.items()if n.startswith(('PackSizeGauge','PackNTCHeadR32','PackNTCLeadStub','PackNTCContactFilm'))};reservehits=[];reservepairs=0
for n,a in reservations.items():
 for m,b in physical.items():
  if m in module:continue
  reservepairs+=1;v=vol(a,b)
  if v>1e-5:reservehits.append({'reservation':n,'fixed':m,'intersection_mm3':v})
meshes={};sectionmeshes={};sectionbox=Part.makeBox(100,150,100,A.Vector(-100,-20,-50))
for n in r['new_roles']+['PCBOnlyKeeperR25','BodyPCB_R17']:
 for suffix,s in [('',physical[n])]+([('-section',physical[n].copy().common(sectionbox))]if n in r['new_roles']else[]):
  if s.Volume<1e-7:continue
  f=P/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(f));(sectionmeshes if suffix else meshes)[f.name]=sha(f)
review={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'reviewer_sha256':sha(Path(__file__)),'source_R31_native_sha256':r['source_R31_native_sha256'],'saved_roles':roles,'source_roles_conserved':conserved,'external_document_links':external,'source_carrier_removed_mm3':removed.Volume,'removal_outside_declared_tools_mm3':outside,'protected_material_witnesses':protected,'new_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':interfaces,'rigid_vs_reservation_pairs':reservepairs,'unexpected_rigid_vs_reservation_intersections':reservehits,'new_meshes_sha256':meshes,'native_X_nonpositive_section_meshes_sha256':sectionmeshes,'scope':'Fresh forced native history, unchanged source material and current physical/nominal-mate geometry. Unchanged source sizing allowance is a reservation, not a second physical battery; nominal pack gauge, sensor parts and their common position budget are distinct. Tape/bond, actual pack limits, stress/vibration/thermal response, actual fasteners/materials remain unqualified.'};(P/'saved-review.json').write_text(json.dumps(review,indent=2)+'\n');assert not hits and not reservehits,(hits,reservehits)
def pose(moving,fixed,delta=(0,0,0),angle=0):
 bad=[]
 for n,a in moving.items():
  a=a.copy()
  if angle:a.rotate(A.Vector(),A.Vector(0,1,0),angle)
  a.translate(A.Vector(*delta))
  for m,b in fixed.items():
   if tuple(sorted([n,m]))in named:continue
   v=vol(a,b)
   if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
 return bad
def stages(name,moving,fixed,offsets,axis,base=(0,0,0)):
 rows=[]
 for t in offsets:
  d=list(base);d[axis]+=t;bad=pose(moving,fixed,d);rows.append({'offset_xyz_mm':d,'hits':bad});print(name,d,bad,flush=True)
 return rows
carrier={'PackRetainingCarrierR32':physical['PackRetainingCarrierR32']};lid={'PackLidR32':physical['PackLidR32']};screw={'PackLidScrewEnvelopeR32':physical['PackLidScrewEnvelopeR32']};assembly={}
assembly['pack_module_top_loading_PCB_lid_waiting']=stages('pack down',module,carrier,[18,12,8,5,3,2,1,.5,0],2)
assembly['lid_top_loading_at_Y_plus2_PCB_waiting']=stages('lid down',lid,dict(carrier,**module),[15,10,5,3,1,.5,.1,0],2,(0,2,0))
assembly['lid_rearward_tongue_engagement']=stages('lid slide',lid,dict(carrier,**module),[2,1.5,1,.5,.25,0],1)
assembly['pack_lid_screw_listed_approach']=stages('lid screw',screw,dict(carrier,**module,**lid),[10,5,2,1,0],2)
body={n:s for n,s in physical.items()if n=='BodyPCB_R17'or(n.startswith('R17_')and n in r['parts']and r['parts'][n]['bounds_xyz_mm'][1]>=25)}
fixed=dict(carrier,**module,**lid,**screw)
assembly['body_PCB_top_loading_pack_lid_fitted']=stages('PCB down',body,fixed,[12,8,4,2,1,.5,.25,0],2)
assembly['original_PCB_keeper_top_loading']=stages('PCB keeper down',{'PCBOnlyKeeperR25':physical['PCBOnlyKeeperR25']},dict(fixed,**body),[12,8,4,2,1,.5,.25,0],2)
# Six common translations are positioning studies, not pouch deformation.
position=[];blockers=[];frame=dict(carrier,**lid);other={n:s for n,s in physical.items()if n not in module}
for axis in range(3):
 for sign in [-1,1]:
  d=[0,0,0];d[axis]=.5*sign;position.append({'offset_xyz_mm':d,'hits':pose(module,other,d)})
  d[axis]=sign;bad=pose({'PackSizeGaugeR32':module['PackSizeGaugeR32']},frame,d);blockers.append({'rigid_gauge_offset_xyz_mm':d,'frame_contacts':bad,'blocked':bool(bad)})
# The existing PCB keeper and the motor remain separate. All tip/motor and
# long wire assemblies wait while the rigid cartridge enters the body.
cartridge=dict(fixed,**body,PCBOnlyKeeperR25=physical['PCBOnlyKeeperR25'])
for n in ['KeeperScrew_1','KeeperScrew1']:
 cartridge[n]=physical[n]
for n,s in physical.items():
 if n.startswith('R17Mate_')and n in r['mates']and r['mates'][n]['bounds_xyz_mm'][1]>20:cartridge[n]=s
assembly['rigid_cartridge_vs_body_only_harnesses_waiting']=stages('cartridge',cartridge,{'KeyedBodyR25':physical['KeyedBodyR25']},list(range(100,-1,-5)),1)
motor={n:physical[n]for n in ['ShellMotorMountR25','MotorClampScrewR25','MotorClampNutR25','MotorMaxEnvelope','MotorLeadFlareAllowanceR21']}
assembly['motor_module_vs_new_pack_parts']=stages('motor',motor,{n:physical[n]for n in r['new_roles']},[100,80,60,40,20,10,5,2,1,.5,.25,0],1)
cap=[]
for y in [20,5,1,.25,0]:
 for angle in [0,90,180,270]:cap.append({'Y_offset_mm':y,'angle_deg':angle,'hits':pose({'MotorSeatCapR25':physical['MotorSeatCapR25']},{n:physical[n]for n in r['new_roles']},(0,y,0),angle)})
shaft=Part.makeCylinder(1.1,16,A.Vector(-11.2,59,-.4),A.Vector(0,0,1));toolhits=[]
for n,s in fixed.items():
 v=vol(shaft,s)
 if v>1e-5:toolhits.append({'fixed':n,'intersection_mm3':v})
allclear=not any(q['hits']for rows in assembly.values()for q in rows)and not any(q['hits']for q in position+cap)and all(q['blocked']for q in blockers)and not toolhits
screen={'native_sha256':before,'saved_review_sha256':sha(P/'saved-review.json'),'screener_sha256':sha(Path(__file__)),'body_PCB_group_count':len(body),'module_roles':list(module),'assembly_stages':assembly,'module_common_position_studies':position,'gauge_only_frame_blocking_probes':blockers,'cap_vs_new_pack_parts_listed_poses':cap,'generic_lid_driver_shaft_hits':toolhits,'all_listed_screens_clear':allclear,'scope':'Finite rigid poses and six positioning/blocking probes only. Pack lid fits before PCB; original keeper stays separate. Gauge-only blockers exclude sensors as load stops. .5mm module shifts are not supplier swelling acceptance. Cartridge test is against metal body only with complete long harnesses, flange, motor and tip waiting; only first4.5mm NTC stubs are modeled. No continuous connected loading, hands, actual drive/thread/preload, deformation, thermal response, adhesive/tape/material or physical qualification.'};(P/'assembly-screen.json').write_text(json.dumps(screen,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('saved pack review',len(roles),'roles',len(conserved),'source roles, static',pairs,'reserve',reservepairs,'stages clear',allclear,flush=True)
