"""Fresh R33 native/source conservation and scoped finite loading screens."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SROOT=ROOT/'hardware/cad/pack-retention-r32/candidate-e';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'geometry-report.json');f=P/'FlangePackR33.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f))
for o in D.Objects:o.touch()
D.recompute()
def bb(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
physical={};reserve={};rows={}
for n,q in dict(r['parts'],**r['mates'],**r['allowances'],**r['co_moving_reservations']).items():
 s=D.getObject(n).Shape.copy();dv=s.Volume-q['volume_mm3'];db=max(abs(x-y)for x,y in zip(bb(s),q['bounds_xyz_mm']));assert s.isValid()and len(s.Solids)==q['solids']and abs(dv)<1e-4 and db<1e-5,(n,dv,db);rows[n]={'valid':True,'solids':len(s.Solids),'volume_delta_mm3':dv,'maximum_bounds_delta_mm':db};(reserve if n in r['co_moving_reservations']else physical)[n]=s
external=[(o.Name,x.Name)for o in D.Objects for x in o.OutList if x.Document!=D];assert not external
sf=SROOT/'PackRetentionR32.FCStd';assert sha(sf)==r['source_R32_native_sha256'];S=A.openDocument(str(sf));conserved={}
for n in r['source_roles_unchanged']:
 a=S.getObject(n).Shape.copy();b=physical[n];same=a.exportBrepToString()==b.exportBrepToString();removed,added=(0.,0.)if same else(a.cut(b.copy()).Volume,b.copy().cut(a).Volume);db=max(abs(x-y)for x,y in zip(bb(a),bb(b)));assert abs(removed)<1e-4 and abs(added)<1e-4 and db<1e-5,(n,removed,added,db);conserved[n]={'exact_BRep_equal':same,'removed_mm3':removed,'added_mm3':added,'maximum_bounds_delta_mm':db}
oldhub=S.getObject('HarnessRightHubR30').Shape.copy();tray=physical['PackSupportHubR33'];lost=oldhub.copy().cut(tray.copy()).Volume;assert abs(lost)<1e-4 and len(tray.Solids)==1,(lost,len(tray.Solids));extension=tray.copy().cut(oldhub.copy());A.closeDocument(S.Name)
named={tuple(sorted([q['a'],q['b']]))for q in r['named_candidate_screw_pilot_interfaces']};seen=set();hits=[];interfaces=[];pairs=0
for n in r['new_roles']:
 for m,b in physical.items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(physical[n],b)
  if v>1e-5:(interfaces if key in named else hits).append({'a':n,'b':m,'intersection_mm3':v})
rh=[];rc=0
for n,s in reserve.items():
 for m,b in physical.items():
  if m in r['module_roles']:continue
  rc+=1;v=vol(s,b)
  if v>1e-5:rh.append({'reservation':n,'fixed':m,'intersection_mm3':v})
assert not hits and not rh,(hits,rh)
def pose(moving,fixed,delta):
 bad=[]
 for n,a in moving.items():
  a=a.copy();a.translate(A.Vector(*delta))
  for m,b in fixed.items():
   if tuple(sorted([n,m]))in named:continue
   v=vol(a,b)
   if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
 return bad
def stage(name,moving,fixed,axis,offsets):
 rr=[]
 for t in offsets:
  d=[0,0,0];d[axis]=t;bad=pose(moving,fixed,d);rr.append({'offset_xyz_mm':d,'hits':bad})
 print(name,'positions',len(rr),'failed',sum(bool(q['hits'])for q in rr),flush=True)
 return rr
module={n:physical[n]for n in r['module_roles']};lid={'PackLidR33':physical['PackLidR33']};screws={n:physical[n]for n in ['PackLidScrewR33_1','PackLidScrewR33_2']};frame={'PackSupportHubR33':tray};fixed_no_cover={n:s for n,s in physical.items()if n not in module and n not in lid and n not in screws and n not in ['FlangeCoverUpper','FlangeCoverLower','ButtonServiceCoverR31','ButtonBezelR31','ButtonBootR31']and not n.startswith(('ButtonPlunger','ButtonHomePin','ButtonStopScrew','ButtonRetainerScrew'))};stages={}
stages['pack_and_attached_sensor_rear_loading_covers_lid_waiting']=stage('module rear approach',module,fixed_no_cover,1,[-30,-20,-12,-8,-5,-3,-2,-1,-.5,0])
stages['lid_rear_approach_covers_waiting']=stage('lid rear approach',lid,dict(fixed_no_cover,**module),1,[-20,-12,-8,-5,-3,-2,-1,-.5,0])
stages['screw_rear_approach_covers_waiting']=stage('screws',screws,dict(fixed_no_cover,**module,**lid),1,[-12,-8,-5,-3,-2,-1,-.5,0])
newonly={n:s for n,s in physical.items()if n in r['new_roles']and n!='PackSupportHubR33'};newonly['PackTrayAdditionR33']=extension
for n,axis,offsets in [('FlangeCoverLower',2,[-30,-20,-12,-8,-4,-2,-1,-.5,0]),('FlangeCoverUpper',2,[30,20,12,8,4,2,1,.5,0]),('ButtonServiceCoverR31',1,[-30,-20,-12,-8,-4,-2,-1,-.5,0])]:stages[n+'_vs_new_pack_parts_only']=stage(n,{n:physical[n]},newonly,axis,offsets)
hubfixed={n:s for n,s in fixed_no_cover.items()if n!='PackSupportHubR33'and not n.startswith(('HubBolt','HubNut'))};stages['added_tray_only_right_hub_closure']=stage('added tray hub closure',{'PackTrayAdditionR33':extension},hubfixed,0,[30,20,12,8,4,2,1,.5,0])
positions=[]
for axis,sign in itertools.product(range(3),[-1,1]):
 d=[0,0,0];d[axis]=.5*sign;positions.append({'offset_xyz_mm':d,'hits':pose(module,{n:s for n,s in physical.items()if n not in module},d)})
tools=[]
for i,z in [(1,-12.4),(2,12.4)]:
 shaft=Part.makeCylinder(1.1,16,A.Vector(18,-27,z),A.Vector(0,-1,0));tools.append({'screw':i,'shaft_diameter_length_mm':[2.2,16],'axis_xyz':[0,-1,0],'hits':pose({'generic_driver':shaft},dict(fixed_no_cover,**module,**lid),(0,0,0))})
allclear=not any(q['hits']for rr in stages.values()for q in rr)and not any(q['hits']for q in positions+tools)
meshes={};sectionmeshes={};clip=Part.makeBox(150,100,100,A.Vector(-50,-18,-50));meshroles=r['new_roles']+['FlangeCoverUpper','FlangeCoverLower','ButtonServiceCoverR31','FlangePCB_R17','KeyedBodyR25','MotorSeatCapR25','MotorMaxEnvelope','ShellMotorMountR25','BodyPCB_R17','PCBOnlyKeeperR25','ButtonSupportHubR31']
for n in meshroles:
 for suffix,s in [('',physical[n]),('-section',physical[n].copy().common(clip))]:
  if s.Volume<1e-7:continue
  p=P/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(p));(sectionmeshes if suffix else meshes)[p.name]=sha(p)
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'reviewer_sha256':sha(Path(__file__)),'saved_roles':rows,'external_document_links':external,'source_roles_conserved':conserved,'source_right_hub_removed_mm3':lost,'right_hub_with_tray_solids':len(tray.Solids),'tray_addition_mm3':extension.Volume,'new_physical_pairs':pairs,'unexpected_intersections':hits,'named_candidate_screw_pilot_interfaces':interfaces,'rigid_reservation_pairs':rc,'unexpected_reservation_intersections':rh,'assembly_stages':stages,'module_common_position_studies':positions,'generic_rear_driver_shaft_studies':tools,'all_listed_screens_clear':allclear,'meshes_sha256':meshes,'native_Y_at_least_minus18_section_meshes_sha256':sectionmeshes,'scope':'Fresh forced native history and source conservation; scoped static and finite rigid approaches. Current old wires preserved, not a completed pack/NTC adapter. Hub closure checks ONLY added tray material; source hub still requires R30 parked loose-end order. Covers check new parts only, not general sealing/closure acceptance. Generic driver shafts do not model actual sockets/hands. Published pack-body size and engineering budget only; no controlled max/growth, soft pouch/load, actual leads/connector, process/material, thermal/electrical/runtime/physical acceptance.'}
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(f)==before;print('SAVED REVIEW',len(rows),'roles,',len(conserved),'source conserved, stages clear',allclear,flush=True)
