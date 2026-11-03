"""Independent metal motor clamp captured at the shell mouth, not by PCB.

Candidate geometry: keyed flange seated on the body rim, cap shoulder clamps
it axially. A single split sleeve and one M2 screw/nut budget grip the motor.
Contact/preload/material/tolerances are design inputs needing qualification.
"""
from pathlib import Path
import sys,json,hashlib,itertools,math
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher,MeshPart
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'hardware/cad/motor-retention-r21/candidate-c'
OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True)
assert not any(OUT.iterdir()),'Preserve executed candidates'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((SOURCE/'geometry-report.json').read_text());nf=Path(sys.argv[1]).resolve()
assert sha(nf)==r['native_sha256']
D=A.openDocument(str(nf));original={n:D.getObject(n).Shape.copy()for n in r['parts']}

def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def cyl(n,radius,y,length,z=0):
 o=D.addObject('Part::Cylinder',n);o.Radius=radius;o.Height=length;o.Placement=A.Placement(A.Vector(0,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
def zcyl(n,radius,x,y,z,length):
 o=D.addObject('Part::Cylinder',n);o.Radius=radius;o.Height=length;o.Placement.Base=A.Vector(x,y,z);return o
def op(n,kind,a,b):
 o=D.addObject('Part::'+kind,n);o.Base=a;o.Tool=b;o.Refine=True;return o
def fuse(n,items):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=items;o.Refine=True;return o
def ring(n,outer,inner,y,length,z=0):
 return op(n,'Cut',cyl(n+'Outer',outer,y,length,z),cyl(n+'Inner',inner,y-.05,length+.1,z))
def hexagon(n,af,x,y,z,h):
 sk=D.addObject('Sketcher::SketchObject',n+'Outline');sk.Placement.Base=A.Vector(x,y,z);rad=af/math.sqrt(3)
 pts=[A.Vector(rad*math.cos(i*math.pi/3),rad*math.sin(i*math.pi/3),0)for i in range(6)]
 for a,b in zip(pts,pts[1:]+pts[:1]):sk.addGeometry(Part.LineSegment(a,b),False)
 o=D.addObject('Part::Extrusion',n);o.Base=sk;o.Dir=A.Vector(0,0,1);o.LengthFwd=h;o.Solid=True;return o

# Remove motor supports from the electronics carrier's native graph.
removed=['MotorSaddle56_5','MotorSaddle78_5','MotorSupportStem','TrayToMotorBridge']
blank=D.getObject('ConnectedCarrierBlank');blank.Shapes=[o for o in blank.Shapes if o.Name not in removed]
pcbkeeper=fuse('PCBOnlyKeeperR25',[D.getObject(n)for n in ['OpenBottomKeeperR21','KeeperUpperPlugBridgeR21','KeeperCentralPlugBridgeR21','MotorKeeperFootR21_1','MotorKeeperFootR211']])
pcbkeeper.Label='PCB-only keeper / plug-loading bridges / independent of motor'
carrier=D.getObject('PortedCarrierR20');carrier.Label='Electronics carrier / motor saddles and motor bridge removed'

# The front rim is the metal-to-metal vibration path. The small covered key
# slot prevents cap closing torque from winding motor/tip leads.
keytool=cyl('CoveredMouthKeySlotR25',1.2,55.5,1.31,14.2)
body=op('KeyedBodyR25','Cut',D.getObject('KeyedOnePieceBody'),keytool)
capshoulder=ring('CapClampShoulderR25',17.5,15.5,57.8,.8)
cap=fuse('MotorSeatCapR25',[D.getObject('FullerClosingCap'),capshoulder])
R10=ROOT/'hardware/cad/front-load-r10/candidate-c'
thread_source=json.loads((R10/'geometry-report.json').read_text())
assert sha(R10/'build.py')==thread_source['builder_sha256']
assert D.getObject('PreservedCapCavityTools').SourceNativeSHA256==thread_source['native_sha256']
pitch=thread_source['study_inputs']['ThreadPitch'];assert pitch==.75
cap.Placement=A.Placement(A.Vector(0,.1,0),A.Rotation(A.Vector(0,1,0),360*.1/pitch))

flange=ring('MotorMountFlangeR25',16.3,15.5,56.8,1.1)
key=fuse('MotorMountKeyR25',[cyl('MotorMountRoundedKeyR25',1.1,55.6,1.3,14.2),box('MotorMountKeyJoinR25',[-1.0,56.8,14.5,1.0,57.2,16.25])])
upright=box('MotorMountUprightR25',[-1.5,57.0,9.1,1.5,57.8,15.9])
beam=box('MotorMountBeamR25',[-1.5,57.5,9.1,1.5,87.0,10.3])
sleeve=cyl('MotorSleeveOuterR25',6.4,62.0,26.3,3.5)
front=ring('MotorFrontStopR25',6.2,4.8,88.3,.4,3.5)
lower=box('MotorClampLowerEarR25',[5.1,71.5,-1.3,11.5,78.0,2.9])
upper=box('MotorClampUpperEarR25',[5.1,72.0,4.1,10.8,77.5,6.8])
mountblank=fuse('MotorMountBlankR25',[flange,key,upright,beam,sleeve,front,lower,upper])
bore=cyl('MotorClampBoreR25',5.6,61.9,26.4,3.5)
slot=box('MotorClampSplitR25',[4.5,61.9,2.9,12,88.8,4.1])
hole=zcyl('MotorClampScrewClearanceR25',1.1,8.2,74.75,-2,12)
pocket=hexagon('MotorClampNutPocketR25',4.15,8.2,74.75,-1.4,2.2)
corner_reliefs=[zcyl('MotorNutPocketCornerReliefR25_'+str(i),.3,8.2+4.15/math.sqrt(3)*math.cos(i*math.pi/3),74.75+4.15/math.sqrt(3)*math.sin(i*math.pi/3),-1.4,2.2)for i in range(6)]
mount=op('ShellMotorMountR25','Cut',mountblank,fuse('MotorMountCutToolsR25',[bore,slot,hole,pocket]+corner_reliefs))
mount.Label='Metal motor mount / keyed rim flange / independent split clamp'
mount.addProperty('App::PropertyString','EngineeringScope')
mount.EngineeringScope='Proposed metal clamp; bore11.2 against capsule11.1max; one M2x8 budget/AF4nut. Material, elastic closure, preload, screw/nut drawings, surface, tolerances and load remain to qualify. No isolating liner selected.'
shaft=zcyl('MotorClampScrewShaftR25',1.0,8.2,74.75,-1.2,8.0)
head=zcyl('MotorClampScrewHeadR25',1.9,8.2,74.75,6.8,2.0)
screw=fuse('MotorClampScrewR25',[shaft,head])
nut=op('MotorClampNutR25','Cut',hexagon('MotorClampNutBlankR25',4.0,8.2,74.75,-.8,1.6),zcyl('MotorClampNutHoleR25',1.1,8.2,74.75,-.9,1.8))
D.recompute()

def inv(s):
 b=s.optimalBoundingBox(False,False)
 return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def volume(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0
 return a.copy().common(b.copy()).Volume

parts={n:D.getObject(n)for n in r['parts']if n not in ['MotorKeeperR21','KeyedOnePieceBody','FullerClosingCap']}
parts.update({o.Name:o for o in [body,cap,pcbkeeper,mount,screw,nut]})
mates={n:D.getObject(n)for n in r['mates']}
flare=D.getObject('MotorLeadFlareAllowanceR21')
changed=['PortedCarrierR20','MotorKeeperR21','KeyedOnePieceBody','FullerClosingCap']
for n,o in parts.items():
 assert o.Shape.isValid()and len(o.Shape.Solids)==(len(original[n].Solids)if n in original and n not in changed else 1),(n,inv(o.Shape))
assert len(pcbkeeper.Shape.Solids)==1
preserved={}
for n,s in original.items():
 if n in changed:continue
 a=parts[n].Shape
 equal=s.exportBrepToString()==a.exportBrepToString()
 removed_v,added_v=(0,0)if equal else(s.copy().cut(a.copy()).Volume,a.copy().cut(s.copy()).Volume)
 assert removed_v<1e-4 and added_v<1e-4,(n,removed_v,added_v)
 preserved[n]={'removed_mm3':removed_v,'added_mm3':added_v,'exact_BRep_equal':equal}
hits=[];named=[];pairs=0
for (n,o),(m,p)in itertools.combinations(parts.items(),2):
 pairs+=1;v=volume(o.Shape,p.Shape)
 if v<1e-5:continue
 row={'a':n,'b':m,'intersection_mm3':v}
 if 'PortedCarrierR20'in [n,m]and any(k.startswith('KeeperScrew')for k in [n,m]):named.append(row)
 else:hits.append(row)
matehits=[];flarehits=[]
for n,o in mates.items():
 for m,p in parts.items():
  if m=='R17_'+n.removeprefix('R17Mate_'):continue
  v=volume(o.Shape,p.Shape)
  if v>1e-5:matehits.append({'mate':n,'target':m,'intersection_mm3':v})
for n,o in dict(parts,**mates).items():
 if n=='MotorMaxEnvelope':continue
 v=volume(flare.Shape,o.Shape)
 if v>1e-5:flarehits.append({'target':n,'intersection_mm3':v})
print('static',pairs,'unexpected',hits,'mates',matehits,'flare',flarehits,flush=True)

# Saved geometry survives even if a later motion check finds a failure.
output=OUT/'ShellMotorMountR25.FCStd';D.Label='R25 / independent shell-coupled motor clamp / DEVELOPMENT'
D.saveAs(str(output))
out={'builder_sha256':sha(Path(__file__)),'source_native_sha256':r['native_sha256'],'source_report_sha256':sha(SOURCE/'geometry-report.json'),
 'native_sha256':sha(output),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':{n:inv(o.Shape)for n,o in mates.items()},'allowances':{flare.Name:inv(flare.Shape)},
 'removed_motor_support_features':removed,'preserved_roles':preserved,'static_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':named,'nominal_mate_intersections':matehits,'conditional_flare_intersections':flarehits,
 'cap_assembly':{'Y_translation_mm':.1,'Y_rotation_deg':360*.1/pitch,'thread_pitch_mm':pitch,'thread_source_report_sha256':sha(R10/'geometry-report.json'),'thread_source_builder_sha256':sha(R10/'build.py'),'scope':'Cap shifted and correctly phased along inherited right-handed thread. Integral1.1mm mount flange creates0.1mm nominal stand-off before old exterior shoulder stop. Provisional profile, tolerances, preload and seal remain unqualified.'},
 'nominal_interfaces':{'motor_bore_diameter_mm':11.2,'motor_capsule_max_diameter_mm':11.1,'sleeve_outer_diameter_mm':12.8,'sleeve_split_gap_mm':1.2,'flange_radial_span_mm':[15.5,16.3],'flange_Y_span_mm':[56.8,57.9],'body_rim_Y_mm':56.8,'cap_shoulder_Y_mm':57.9,'cap_shoulder_ID_mm':31.0,'nut_pocket_corner_relief_radius_mm':.3,'minimum_ear_X_wall_after_relief_mm':11.5-(8.2+4.15/math.sqrt(3)+.3),'internal_key_tool_radius_mm':1.2,'internal_key_tool_center_Z_mm':14.2,'one_screw_budget':'M2x8,3.8diamx2head; unqualified geometry','one_nut_budget':'M2 AF4,1.6thick; clearance hole, no actual thread'},
 'scope':'Independent metal motor clamp captured on body rim by added cap shoulder; keyed against rotation; no motor load through PCB keeper. Nominal envelopes/conditional flare only. Material, elastic preload/force, controlled fastener/motor geometry, surface/seals/tolerances, wires and physical assembly remain open. Battery OPEN.'}
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')

# Separate motor-module installation after the electronics cartridge. The cap
# and stationary tip source roles wait; that tip still needs a support design.
module=[mount,screw,nut,D.getObject('MotorMaxEnvelope'),flare]
fixed=[o for n,o in parts.items()if n not in [q.Name for q in module]+[cap.Name,'TipPCB','TipComponentEnvelope','TipThermalShoe']]+list(mates.values())
loading=[]
for y in [100,80,60,40,20,10,5,2,1,.5,.25,0]:
 bad=[]
 for o in module:
  s=o.Shape.copy();s.translate(A.Vector(0,y,0))
  for p in fixed:
   v=volume(s,p.Shape)
   if v>1e-5:bad.append({'moving':o.Name,'fixed':p.Name,'intersection_mm3':v})
 loading.append({'Y_offset_mm':y,'hits':bad});print('module Y',y,bad,flush=True)
capmotion=[]
for y in [40,20,10,5,2,1,.5,.25,0]:
 for angle in [0,90,180,270]:
  s=cap.Shape.copy();s.rotate(A.Vector(0,0,0),A.Vector(0,1,0),angle);s.translate(A.Vector(0,y,0));bad=[]
  for o in module+[D.getObject(n)for n in ['TipPCB','TipComponentEnvelope','TipThermalShoe']]:
   v=volume(s,o.Shape)
   if v>1e-5:bad.append({'fixed':o.Name,'intersection_mm3':v})
  capmotion.append({'Y_offset_mm':y,'angle_deg':angle,'hits':bad})
print('cap sampled hits',[v for v in capmotion if v['hits']],flush=True)
out['motor_module_listed_loading_poses']=loading;out['cap_to_motor_tip_listed_poses']=capmotion
out['independent_motor_to_PCB_clearance_mm']=mount.Shape.distToShape(carrier.Shape)[0]
out['mount_to_PCB_keeper_clearance_mm']=mount.Shape.distToShape(pcbkeeper.Shape)[0]

motor_loading=[]
for y in [-80,-60,-40,-30,-20,-10,-5,-2,-1,-.5,-.25,0]:
 bad=[]
 for o in [D.getObject('MotorMaxEnvelope'),flare]:
  s=o.Shape.copy();s.translate(A.Vector(0,y,0))
  for p in [mount,screw,nut]:
   v=volume(s,p.Shape)
   if v>1e-5:bad.append({'moving':o.Name,'fixed':p.Name,'intersection_mm3':v})
 motor_loading.append({'Y_offset_mm':y,'hits':bad})
out['motor_into_clamp_listed_poses']=motor_loading
print('motor insertion hits',[v for v in motor_loading if v['hits']],flush=True)

bodyparts=[D.getObject(n)for n in r['cartridge_roles']if n.startswith('R17_')or n=='BodyPCB_R17']
board_drop=[];keeper_drop=[]
for z in [12,8,4,2,1,.5,.25,0]:
 bad=[]
 for o in bodyparts:
  s=o.Shape.copy();s.translate(A.Vector(0,0,z))
  for p in [carrier,D.getObject('NarrowPackAllowance')]:
   v=volume(s,p.Shape)
   if v>1e-5:bad.append({'moving':o.Name,'fixed':p.Name,'intersection_mm3':v})
 board_drop.append({'Z_offset_mm':z,'hits':bad})
 s=pcbkeeper.Shape.copy();s.translate(A.Vector(0,0,z));bad=[]
 for p in [carrier,D.getObject('NarrowPackAllowance')]+bodyparts+list(mates.values()):
  v=volume(s,p.Shape)
  if v>1e-5:bad.append({'fixed':p.Name,'intersection_mm3':v})
 keeper_drop.append({'Z_offset_mm':z,'hits':bad})
out['board_drop_listed_poses']=board_drop;out['PCB_keeper_drop_listed_poses']=keeper_drop
print('board/keeper drop hits',[v for v in board_drop+keeper_drop if v['hits']],flush=True)

def plane_contact(a,b,y):
 af=[f for f in a.Faces if f.BoundBox.YLength<1e-5 and abs(f.BoundBox.YMin-y)<1e-5]
 bf=[f for f in b.Faces if f.BoundBox.YLength<1e-5 and abs(f.BoundBox.YMin-y)<1e-5]
 return sum(x.copy().common(v.copy()).Area for x in af for v in bf)
out['nominal_coplanar_contact_area_mm2']={'body_rim_to_motor_mount':plane_contact(body.Shape,mount.Shape,56.8),'cap_shoulder_to_motor_mount':plane_contact(cap.Shape,mount.Shape,57.9)}
out['contact_scope']='Coincident nominal planar face areas only; no actual preload/contact pressure, tolerance, thread fit, seal, stiffness or vibration-transfer qualification. Integral flange gives nominal0.1mm stop priority; prove it survives the actual tolerance stack and surface finishing.'
print('nominal contact',out['nominal_coplanar_contact_area_mm2'],flush=True)
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')
meshes={};section=Part.makeBox(200,250,100,A.Vector(-100,-100,-100))
for n,o in dict(parts,**mates,**{flare.Name:flare}).items():
 for suffix,s in [('',o.Shape)]+([('-section',o.Shape.copy().common(section.copy()))]if n in [body.Name,cap.Name]else[]):
  if s.Volume<1e-6:continue
  f=OUT/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
out['review_meshes_sha256']=meshes;(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name);assert sha(nf)==r['native_sha256']
print('saved',output,flush=True)
