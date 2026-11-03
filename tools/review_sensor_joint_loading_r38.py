"""Saved R38 sensor retention: source material, staged loading and hard blockers."""
from pathlib import Path
import hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SOURCE=ROOT/'hardware/cad/pack-assembly-r37/power-f';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());sr=json.loads((SOURCE/'geometry-report.json').read_text());path=P/'RetainedSensorJointsR38.FCStd';source=SOURCE/'ConditionalPackPowerR37.FCStd';before=sha(path);assert before==r['native_sha256']and sha(source)==r['source_R37F_sha256']==sr['native_sha256'];D=A.openDocument(str(path));S=A.openDocument(str(source))
def volume(s):return 0. if s.isNull()else s.Volume
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return volume(a.copy().common(b.copy()))
def eq(a,b):
 minus=volume(a.copy().cut(b.copy()));plus=volume(b.copy().cut(a.copy()));assert max(abs(minus),abs(plus))<1e-4,(minus,plus)
 return {'removed_mm3':minus,'added_mm3':plus}
fast=[];material=[]
with zipfile.ZipFile(path)as dz,zipfile.ZipFile(source)as sz:
 def poses(z):
  root=ET.fromstring(z.read('Document.xml'));return{o.get('name'):ET.tostring(o.find("Properties/Property[@name='Placement']"))if o.find("Properties/Property[@name='Placement']")is not None else None for o in root.findall('ObjectData/Object')}
 dp,sp=poses(dz),poses(sz)
 for name in dict.fromkeys(sr['fixed_roles']+list(sr['new_roles'])):
  member=name+'.Shape.brp'
  if member in dz.namelist()and member in sz.namelist()and dz.read(member)==sz.read(member)and dp[name]==sp[name]:fast.append(name)
  else:material.append({'name':name,**eq(S.getObject(name).Shape.copy(),D.getObject(name).Shape.copy())})
base=S.getObject(r['replaced_hub']).Shape.copy();post=D.getObject('JointCombPostR38').Shape.copy();pocket=D.getObject('JointCombHubPocketR38').Shape.copy();pilot=D.getObject('JointCombPilotR38').Shape.copy();slot=D.getObject('JointCombKeySlotR38').Shape.copy();hub=D.getObject('JointRetainingHubR38').Shape.copy();expected=base.copy().cut(pocket.copy()).fuse(post.copy()).cut(pilot.copy()).cut(slot.copy());hubproof=eq(expected,hub)
witnesses={}
regions={'capture_Y_at_least_minus8':Part.makeBox(120,108,120,A.Vector(-60,-8,-60))}
for z,label in [(5.5,'upper_bolt_end_seats'),(-13.5,'lower_bolt_end_seats')]:regions[label]=Part.makeBox(5.5,6,8,A.Vector(-13,-14.5,z)).fuse(Part.makeBox(5.5,6,8,A.Vector(7.5,-14.5,z)))
for i in [1,2]:regions['pack_lid_post_'+str(i)]=S.getObject('PackLidPostR33_'+str(i)).Shape.copy()
for name,region in regions.items():
 witness=base.copy().common(region.copy());loss=volume(witness.copy().cut(hub.copy()));assert loss<1e-5,(name,loss);witnesses[name]={'source_region_mm3':volume(witness),'lost_mm3':loss}
allparts={n:D.getObject(n).Shape.copy()for n in r['fixed_roles']+list(r['new_roles'])}
waiting=['FlangeCoverLower','FlangeCoverUpper','ButtonServiceCoverR31']
stages=[]
def stage(label,moving,axis,offsets,extra_wait):
 fixed={n:s for n,s in allparts.items()if n not in moving+waiting+extra_wait};poses=[]
 for offset in offsets:
  hits=[]
  for n in moving:
   s=allparts[n].copy();s.translate(A.Vector(*axis)*offset)
   for m,t in fixed.items():
    v=overlap(s,t)
    if v>1e-5:hits.append({'moving':n,'fixed':m,'intersection_mm3':v})
  poses.append({'offset_mm':offset,'unexpected_hits':hits})
  print(label,offset,hits,flush=True)
 stages.append({'stage':label,'moving':moving,'axis':axis,'waiting':waiting+extra_wait,'poses':poses})
combpads=[n for n in r['new_roles']if n.startswith('JointCombSoftPadR38_')]
stage('Top-load return pad and separate plug',['ReturnJointSoftPadR38','ReturnJointDropInPlugR38'],[0,0,1],[0,.1,.2,.5,1,2,4,8,12,16],['SensorJointCombR38','JointCombScrewEnvelopeR38']+combpads)
stage('Front-load shared comb with four preattached pad targets',['SensorJointCombR38']+combpads,[0,1,0],[0,.1,.2,.5,1,2,3,4],['JointCombScrewEnvelopeR38'])
# Generic tool starts at the candidate screw's head face, co-axial to its Y
# axis. It is deliberately a bounded probe, not a selected real screwdriver.
tool=Part.makeCylinder(.7,2,A.Vector(19.8,-9.3,7),A.Vector(0,1,0)).fuse(Part.makeCylinder(1.5,10,A.Vector(19.8,-7.3,7),A.Vector(0,1,0)));toolposes=[]
for offset in [0,1,2,4,8]:
 s=tool.copy();s.translate(A.Vector(0,offset,0));hits=[]
 for n,t in allparts.items():
  if n in waiting:continue
  v=overlap(s,t)
  if v>1e-5:hits.append({'fixed':n,'intersection_mm3':v})
 toolposes.append({'offset_mm':offset,'unexpected_hits':hits})
# Hard geometry only: compliant pads are excluded from blocker claims.
blockers=[];retainers={'hub':hub,'comb':D.getObject('SensorJointCombR38').Shape.copy(),'return_plug':D.getObject('ReturnJointDropInPlugR38').Shape.copy()}
for target in [q['joint']for q in r['nominal_joint_pad_contacts']]:
 rows=[];s=D.getObject(target).Shape.copy()
 for axis in range(3):
  for sign in [-1,1]:
   first=None
   for step in range(1,41):
    distance=.05*step;vec=[0,0,0];vec[axis]=sign*distance;moving=s.copy();moving.translate(A.Vector(*vec));hits=[{'retainer':n,'intersection_mm3':v}for n,t in retainers.items()if(v:=overlap(moving,t))>1e-5]
    if hits:first={'distance_mm':distance,'hits':hits};break
   rows.append({'axis':'XYZ'[axis],'sign':sign,'first_sampled_hard_blocker':first})
 blockers.append({'joint':target,'directions':rows})
print('hard-blocker screens finished',flush=True)
key_blockers=[]
for sign in [-1,1]:
 first=None
 for step in range(1,21):
  angle=sign*step*.1;moving=D.getObject('JointCombKeyR38').Shape.copy();moving.rotate(A.Vector(19.8,-12.1,7.),A.Vector(0,1,0),angle);v=overlap(moving,hub)
  if v>1e-5:first={'angle_degrees':angle,'intersection_mm3':v};break
 key_blockers.append({'sign':sign,'first_sampled_key_to_hub_blocker':first})
out={'native_sha256':before,'source_R37F_sha256':sha(source),'reviewer_sha256':sha(Path(__file__)),'source_roles_conserved':len(fast)+len(material),'source_BRep_and_placement_matches':fast,'source_material_comparisons':material,'hub_equals_declared_source_cut_plus_post_minus_pilot_and_key_slot':hubproof,'hub_source_removed_mm3':volume(base.copy().cut(hub.copy())),'hub_added_mm3':volume(hub.copy().cut(base.copy())),'protected_material':witnesses,'staged_loading':stages,'generic_tool':{'tip_D_mm':1.4,'tip_L_mm':2,'shaft_D_mm':3,'shaft_L_mm':10,'poses':toolposes},'joint_hard_blocker_probes':blockers,'key_rotation_probes':key_blockers,'all_key_rotation_samples_blocked_within_2degrees':all(q['first_sampled_key_to_hub_blocker']is not None for q in key_blockers),'all_listed_loading_and_tool_poses_clear':all(not q['unexpected_hits']for s in stages for q in s['poses'])and all(not q['unexpected_hits']for q in toolposes),'all_joint_six_direction_samples_blocked_within_2mm':all(q['first_sampled_hard_blocker']is not None for b in blockers for q in b['directions']),'scope':'Fresh saved source/material review, named capture/end-seat/lid-post material, listed staged rigid loading/tool poses, joint-budget translation blockers and integral-key rotation samples. Not continuous motion, actual tool/fastener tolerance, soft pad preload/joint strength, key torque, creep or physical assembly proof. Covers wait; full connected assembly and power-side retention remain separate.'};(P/'loading-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);A.closeDocument(S.Name);assert sha(path)==before and sha(source)==r['source_R37F_sha256'];print('SAVED load/tool clear',out['all_listed_loading_and_tool_poses_clear'],'all hard blockers',out['all_joint_six_direction_samples_blocked_within_2mm'],'key blockers',key_blockers,flush=True)
