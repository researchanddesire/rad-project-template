"""Read-only review of the integrated R39 power route and local retainers."""
from pathlib import Path
import hashlib,itertools,json,sys,zipfile,xml.etree.ElementTree as ET
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SOURCE=ROOT/'hardware/cad/joint-retention-r38/sensor-c';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());sr=json.loads((SOURCE/'geometry-report.json').read_text());gr=json.loads((ROOT/'hardware/cad/power-retention-r39/power-g/geometry-report.json').read_text());kr=json.loads((ROOT/'hardware/cad/power-retention-r39/mate-k/geometry-report.json').read_text());path=P/'RetainedPackPowerR39.FCStd';sp=SOURCE/'RetainedSensorJointsR38.FCStd';before=sha(path);assert before==r['native_sha256']and r['all_static_screens_clear'];assert sha(sp)==sr['native_sha256']==gr['source_R38C_sha256'];D=A.openDocument(str(path));S=A.openDocument(str(sp))
def volume(s):return 0. if s.isNull()else s.Volume
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return volume(a.copy().common(b.copy()))
def eq(a,b):
 minus=volume(a.copy().cut(b.copy()));plus=volume(b.copy().cut(a.copy()));assert max(abs(minus),abs(plus))<1e-4,(minus,plus);return {'lost_mm3':minus,'added_mm3':plus}
def shape(n):return D.getObject(n).Shape.copy()
fast=[];material=[]
with zipfile.ZipFile(path)as dz,zipfile.ZipFile(sp)as sz:
 def poses(z):
  root=ET.fromstring(z.read('Document.xml'));return{o.get('name'):ET.tostring(o.find("Properties/Property[@name='Placement']"))if o.find("Properties/Property[@name='Placement']")is not None else None for o in root.findall('ObjectData/Object')}
 dp,spose=poses(dz),poses(sz)
 for name in dict.fromkeys(sr['fixed_roles']+list(sr['new_roles'])):
  member=name+'.Shape.brp'
  if member in dz.namelist()and member in sz.namelist()and dz.read(member)==sz.read(member)and dp[name]==spose[name]:fast.append(name)
  else:material.append({'name':name,**eq(S.getObject(name).Shape.copy(),shape(name))})
print('source object shapes conserved',len(fast)+len(material),flush=True)
parts={n:shape(n)for n in r['fixed_roles']+list(r['new_roles'])};left='PowerLapRetainingHubR39';right='ForwardWireJointRetainingHubR38';cap='LapCapturingMateLidR39';comb='PowerLapDropInCombR39';screw='MateLidScrewEnvelopeR39'
proposed=set(gr['new_roles'])|set(r['new_roles'])|{right,screw};proposed &= set(parts)
remap={f'PackPowerJointSpaceR39_{i}':f'RetainedPowerJointSpaceR39_{i}'for i in [1,2]};allowed=set()
for q in gr['named_process_interfaces']:
 allowed.add(frozenset([remap.get(q['a'],q['a']),remap.get(q['b'],q['b'])]))
for q in r['named_inherited_or_own_process_interfaces']:allowed.add(frozenset([q['a'],q['b']]))
allowed.add(frozenset([left,screw]));bases={left:S.getObject('PoweredConnectedPackTailLeftHubR34').Shape.copy(),right:S.getObject('JointRetainingHubR38').Shape.copy()};hits=[];inherited=[];checked=set()
for name in sorted(proposed):
 a=parts[name];assert a.isValid()and len(a.Solids)==1,name
 for other,b in parts.items():
  pair=frozenset([name,other])
  if name==other or pair in checked:continue
  checked.add(pair);v=overlap(a,b)
  if v<=1e-5 or pair in allowed:continue
  base=bases.get(name);old=overlap(base,b)if base is not None else 0.;added=volume(a.copy().common(b.copy()).cut(base.copy()))if base is not None else v
  row={'a':name,'b':other,'intersection_mm3':v,'source_overlap_mm3':old,'new_material_overlap_mm3':added}
  (inherited if old>1e-5 and added<1e-5 else hits).append(row)
assert not hits,hits
print('fresh proposed-part comparisons',len(checked),'clear',flush=True)
# Candidate head/nut bearing support derives from the actual source budgets:
# headR1.9 seats atX-8; nut4AF seats atX8. Each witness includes1mm backing.
bearings=[];monitors=[]
for oldname,newname in [('PoweredConnectedPackTailLeftHubR34',left),('JointRetainingHubR38',right)]:
 old=S.getObject(oldname).Shape.copy();current=parts[newname]
 for z,suffix in [(-8,'_1'),(8,'1')]:
  if newname==left:region=Part.makeCylinder(1.9,1.,A.Vector(-8,-11,z),A.Vector(1,0,0))
  else:region=Part.Face(S.getObject('HubNutOuter'+suffix+'Section').Shape.Wires[0]).extrude(A.Vector(-1,0,0))
  witness=old.copy().common(region);loss=volume(witness.copy().cut(current.copy()));assert loss<1e-5,(newname,z,loss);bearings.append({'hub':newname,'bolt_centre_Z_mm':z,'source_bearing_backing_volume_mm3':witness.Volume,'lost_mm3':loss})
  region=Part.makeCylinder(2.2 if newname==left else 2.6,1.,A.Vector(-8 if newname==left else 7,-11,z),A.Vector(1,0,0));w=old.copy().common(region);monitors.append({'hub':newname,'bolt_centre_Z_mm':z,'surrounding_radius_mm':2.2 if newname==left else 2.6,'lost_mm3':volume(w.copy().cut(current.copy()))})
 collar=old.copy().common(Part.makeBox(120,108,120,A.Vector(-60,-8,-60)));loss=volume(collar.copy().cut(current.copy()));assert loss<1e-5
region=Part.makeBox(25,2.9,2.3,A.Vector(-36,-21,-9.2));seat=S.getObject('PoweredConnectedPackTailLeftHubR34').Shape.copy().common(region);seatloss=volume(seat.copy().cut(parts[left].copy()));assert seatloss<1e-5
print('candidate bearing support and board lower seat preserved',flush=True)
routes=[]
for i in [1,2]:
 for prefix,minimum,length in [('StockPackLead',11.,21.8),('SpareMateLead',4.,18.5),('BodyPackPowerWire',4.,None)]:
  name=prefix+'R39_'+str(i);es=D.getObject(name+'Path').Shape.Edges;radii=[e.Curve.Radius for e in es if hasattr(e.Curve,'Radius')];L=sum(e.Length for e in es);assert min(radii)>=minimum-1e-5
  if length is not None:assert abs(L-length)<1e-5
  routes.append({'role':name,'native_path_length_mm':L,'minimum_circle_radius_mm':min(radii)})
wirepairs=[]
for prefix in ['StockPackLead','SpareMateLead','BodyPackPowerWire']:
 a,b=[parts[prefix+'R39_'+str(i)]for i in [1,2]];gap=a.distToShape(b)[0];assert overlap(a,b)<1e-5;wirepairs.append({'pair':prefix,'minimum_jacket_gap_mm':gap})
anchor=Part.makeBox(30,2.2,20,A.Vector(-15,34.9,-15));anchors=[]
for old,new in [('PackConnectedWireR36_1','BodyPackPowerWireR39_1'),('PackConnectedWireR36_3','BodyPackPowerWireR39_2')]:anchors.append({'role':new,**eq(S.getObject(old).Shape.copy().common(anchor.copy()),parts[new].copy().common(anchor.copy()))})
corechecks=[]
for i in [1,2]:
 a,b,s=[parts[p+'R39_'+str(i)]for p in ['SpareMateBare','BodyPackPowerBare','PackPowerSolderBridge']];gap=a.distToShape(b)[0];assert gap>=.09999 and overlap(a,b)<1e-5;assert s.distToShape(a)[0]<1e-5 and s.distToShape(b)[0]<1e-5
 budget=parts['RetainedPowerJointSpaceR39_'+str(i)]
 for q in [a,b,s]:assert volume(q.copy().cut(budget.copy()))<1e-5
 corechecks.append({'pin':i,'bare_gap_mm':gap,'cores_and_solder_target_inside_new_D2p8_budget':True})
waiting=['FlangeCoverLower','FlangeCoverUpper','ButtonServiceCoverR31'];rot=A.Rotation(A.Vector(1,0,0),35);origin=A.Vector(*r['lap_local_geometry']['frame']['centre_xyz_mm']);n=rot.multVec(A.Vector(0,1,0));v=rot.multVec(A.Vector(0,0,1));stages=[]
def stage(label,moving,axis,offsets,absent,pre_offset=None):
 fixed={m:q for m,q in parts.items()if m not in moving+waiting+absent};rows=[]
 for d in offsets:
  bad=[]
  for name in moving:
   q=parts[name].copy();q.translate(axis*d+(pre_offset or A.Vector()))
   for other,t in fixed.items():
    val=overlap(q,t)
    if val>1e-5:bad.append({'moving':name,'fixed':other,'intersection_mm3':val})
  rows.append({'offset_mm':d,'unexpected_hits':bad});print(label,d,bad,flush=True)
 stages.append({'stage':label,'moving':moving,'axis_xyz':list(axis),'pre_offset_xyz_mm':list(pre_offset or A.Vector()),'waiting':waiting+absent,'poses':rows})
stage('Lower lap comb after elevated front approach',[comb],v,[0,.1,.2,.5,1,2,3],[cap,screw])
stage('Front approach with comb raised3mm',[comb],n,[0,1,2,4,6,8],[cap,screw],v*3)
stage('Fit keyed mate lid and comb bridge',[cap],n,[0,.1,.2,.5,1,2,4,6,8,10,12],[screw])
point=origin+rot.multVec(A.Vector(-21,6.1,3.6));tool=Part.makeCylinder(.7,2,point,n).fuse(Part.makeCylinder(1.5,10,point+n*2,n));toolposes=[]
for offset in [0,1,2,4,8]:
 q=tool.copy();q.translate(n*offset);bad=[]
 for name,t in parts.items():
  if name in waiting:continue
  val=overlap(q,t)
  if val>1e-5:bad.append({'fixed':name,'intersection_mm3':val})
 toolposes.append({'offset_mm':offset,'unexpected_hits':bad})
retainers={left:parts[left],cap:parts[cap],comb:parts[comb]};blocks=[]
for target in ['PackMateProcessSpaceR39','RetainedPowerJointSpaceR39_1','RetainedPowerJointSpaceR39_2',comb]:
 rows=[]
 for axis in range(3):
  for sign in [-1,1]:
   first=None
   for k in range(1,41):
    d=.05*k;delta=[0,0,0];delta[axis]=sign*d;q=parts[target].copy();q.translate(A.Vector(*delta));bad=[{'retainer':name,'intersection_mm3':val}for name,t in retainers.items()if name!=target and(val:=overlap(q,t))>1e-5]
    if bad:first={'distance_mm':d,'hits':bad};break
   rows.append({'axis':'XYZ'[axis],'sign':sign,'first_sampled_hard_blocker':first})
 blocks.append({'target':target,'directions':rows})
key=[];pivot=origin+rot.multVec(A.Vector(-21,3.3,3.6))
for sign in [-1,1]:
 first=None
 for k in range(1,21):
  q=shape('MateLidKeyR39');q.rotate(pivot,n,sign*.1*k);val=overlap(q,parts[left])
  if val>1e-5:first={'angle_degrees':sign*.1*k,'intersection_mm3':val};break
 key.append({'sign':sign,'first_sampled_key_blocker':first})
out={'native_sha256':before,'source_R38C_sha256':sha(SOURCE/'RetainedSensorJointsR38.FCStd'),'reviewer_sha256':sha(Path(__file__)),'source_object_shapes_retained':len(fast)+len(material),'source_BRep_and_placement_matches':fast,'source_material_comparisons':material,'fresh_proposed_part_comparisons':len(checked),'unexpected_intersections':hits,'fresh_inherited_interfaces':inherited,'candidate_bearing_backing_checks':bearings,'surrounding_bearing_margin_monitors':monitors,'source_board_lower_seat_region_loss_mm3':seatloss,'source_power_G_broad_hub_box_changes':gr['hub_changes'],'native_route_checks':routes,'native_wire_pair_gaps':wirepairs,'unchanged_body_anchor_sections':anchors,'power_lap_core_checks':corechecks,'staged_loading':stages,'generic_tool':{'tip_D_mm':1.4,'tip_L_mm':2,'shaft_D_mm':3,'shaft_L_mm':10,'poses':toolposes},'hard_blocker_probes':blocks,'key_rotation_probes':key,'all_saved_installed_checks_clear':not hits,'all_listed_loading_and_tool_poses_clear':all(not p['unexpected_hits']for q in stages for p in q['poses'])and all(not q['unexpected_hits']for q in toolposes),'all_targets_six_direction_hard_blockers':all(q['first_sampled_hard_blocker']is not None for b in blocks for q in b['directions']),'all_key_rotation_samples_blocked':all(q['first_sampled_key_blocker']is not None for q in key),'scope':'Fresh nominal installed/source/route/core review and listed staged rigid loading/tool/capture samples. Candidate bolt/nut bearing support is distinguished from explicitly lost material in the older broad lower-hub box. No complete-hub strength, actual fastener/driver fit, housing anti-unmating/contact engagement, pad preload/creep, continuous assembly, electrical, thermal or physical acceptance. Battery OPEN/product BOM unchanged.'};(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);A.closeDocument(S.Name);assert sha(path)==before;print('SAVED installed',out['all_saved_installed_checks_clear'],'stages',out['all_listed_loading_and_tool_poses_clear'],'blockers',out['all_targets_six_direction_hard_blockers'],'key',out['all_key_rotation_samples_blocked'],flush=True)
