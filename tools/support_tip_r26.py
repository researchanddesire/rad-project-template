"""Detachable stationary tip carrier; independent of the motor clamp.

Front-loaded side tongue lets the complete sensor module fit after the motor.
Metal pickup shoe is retained by a candidate fitted E-clip, not PCB thrust.
"""
from pathlib import Path
import sys,json,hashlib,math,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher,MeshPart
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/cad/motor-shell-mount-r25/candidate-d'
OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((SOURCE/'geometry-report.json').read_text());nf=Path(sys.argv[1]).resolve();assert sha(nf)==r['native_sha256']
D=A.openDocument(str(nf));old={n:D.getObject(n).Shape.copy()for n in r['parts']}
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def cyl(n,r,y,h,z=0,x=0):
 o=D.addObject('Part::Cylinder',n);o.Radius=r;o.Height=h;o.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
def zcyl(n,r,x,y,z,h):
 o=D.addObject('Part::Cylinder',n);o.Radius=r;o.Height=h;o.Placement.Base=A.Vector(x,y,z);return o
def op(n,t,a,b):
 o=D.addObject('Part::'+t,n);o.Base=a;o.Tool=b;o.Refine=True;return o
def fuse(n,ls):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=ls;o.Refine=True;return o
def poly(n,pts,z,h):
 sk=D.addObject('Sketcher::SketchObject',n+'Outline');sk.Placement.Base.z=z
 for a,b in zip(pts,pts[1:]+pts[:1]):sk.addGeometry(Part.LineSegment(A.Vector(*a,0),A.Vector(*b,0)),False)
 o=D.addObject('Part::Extrusion',n);o.Base=sk;o.Dir=A.Vector(0,0,1);o.LengthFwd=h;o.Solid=True;return o
def nose(n,rad,axial,cy):
 sk=D.addObject('Sketcher::SketchObject',n+'Meridian');e=Part.Ellipse(A.Vector(0,cy+axial,0),A.Vector(rad,cy,0),A.Vector(0,cy,0));arc=Part.ArcOfEllipse(e,0,math.pi/2)
 sk.addGeometry(arc,False);sk.addGeometry(Part.LineSegment(arc.EndPoint,A.Vector(0,cy,0)),False);sk.addGeometry(Part.LineSegment(A.Vector(0,cy,0),arc.StartPoint),False)
 o=D.addObject('Part::Revolution',n);o.Source=sk;o.Axis=A.Vector(0,1,0);o.Angle=360;o.Solid=True;return o

# Side socket stays outside the narrow body, on the existing tray's front.
receiverblank=op('TipReceiverRoundedBlankR26','Common',box('TipReceiverBoxR26',[-14.1,63.4,-10.4,-9.8,69.8,-1.0]),cyl('TipReceiverRadialLimitR26',15.1,63.3,6.6))
pocket=box('TipReceiverTonguePocketR26',[-13.3,63.6,-6.0,-10.1,69.9,-2.3])
access=zcyl('TipReceiverDriverWindowR26',1.7,-11.8,66.5,-3.0,3.0)
pilot=zcyl('TipReceiverThreadPilotR26',.625,-11.8,66.5,-10.5,4.6)
beamopening=box('TipReceiverBeamOpeningR26',[-13.1,68.8,-2.3,-10.0,69.9,0])
receiver=op('TipReceiverR26','Cut',receiverblank,fuse('TipReceiverCutToolsR26',[pocket,access,pilot,beamopening]))
wireplan=Path(sys.argv[3]).resolve();wp=json.loads(wireplan.read_text());channels=[]
for q in wp['wires']:
 path=D.addObject('Part::Feature','WireCombPathR26_'+str(q['pin']));path.Shape=Part.Wire(edges_from_plan(q))
 profile=D.addObject('Sketcher::SketchObject','WireCombProfileR26_'+str(q['pin']));profile.Placement=A.Placement(A.Vector(*q['J5_wire_exit_nominal_xyz_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),.45),False)
 sweep=D.addObject('Part::Sweep','WireCombChannelR26_'+str(q['pin']));sweep.Sections=[profile];sweep.Spine=path;sweep.Solid=True;sweep.Frenet=True;channels.append(sweep)
combblank=op('WireCombRadialBlankR26','Common',box('WireCombBoxR26',[9.9,66.5,-6,14.5,68.0,2.9]),cyl('WireCombRadialLimitR26',15.0,66.4,1.7))
comb=op('SupportedWireCombR26','Cut',combblank,fuse('WireCombChannelToolsR26',channels))
carrier=fuse('TipReadyCarrierR26',[D.getObject('PortedCarrierR20'),receiver,comb])
carrier.Label='Electronics carrier / detachable tip-module receiver / no motor support'

root=box('TipModuleTongueR26',[-13.1,63.6,-6.0,-10.3,69.5,-2.7])
centres=[(-11.8,69.0),(-8.5,80.0),(-7.0,88.0),(-3.3,93.0)]
beam=poly('TipModuleSideBeamR26',[(x-1,y)for x,y in centres]+[(x+1,y)for x,y in reversed(centres)],-4.8,3.5)
cup=op('TipModuleCupR26','Cut',cyl('TipCupOuterR26',4.4,92.5,2.2),fuse('TipCupVoidsR26',[cyl('TipCupRearBoreR26',3.8,92.4,2.1),cyl('TipCupProbeOpeningR26',1.85,94.4,.4)]))
floor=box('TipStrainReliefFloorR26',[-3.2,91.0,-6.2,3.2,92.4,-5.5])
ribs=[box('TipStrainReliefRibR26_'+str(s),([2.8,92.0,-5.5,3.8,92.7,-2.3]if s>0 else[-3.8,92.0,-5.5,-2.8,92.7,-2.3]))for s in [-1,1]]
blank=fuse('TipModuleBlankR26',[root,beam,cup,floor]+ribs)
rootclear=zcyl('TipModuleRootClearanceR26',.9,-11.8,66.5,-7,5)
wirewindow=box('TipModuleWireWindowR26',[-3.1,91.9,-5.5,3.1,94.5,-2.2])
module=op('StationaryTipCarrierR26','Cut',blank,fuse('TipModuleCutToolsR26',[rootclear,wirewindow]))
module.Label='Detachable stationary tip carrier / side beam and strain-relief floor'

# A single M1.6x6 candidate seats directly on the tongue through the roof window.
screw=fuse('TipCarrierScrewEnvelopeR26',[zcyl('TipCarrierScrewShaftR26',.8,-11.8,66.5,-8.7,6),zcyl('TipCarrierScrewHeadR26',1.6,-11.8,66.5,-2.7,1.6)])
screw.Label='M1.6x6 candidate screw / D3.2 head allowance / pilot thread unqualified'

# Keep the component face rearward. The fitted clip carries cap thrust into
# the cup. Use the loaded shoe pose with .02mm taken up in its groove.
for n in ['TipPCB','TipComponentEnvelope']:
 o=D.getObject(n);o.Placement=A.Placement(A.Vector(0,-.77,0),A.Rotation()).multiply(o.Placement)
smallnose=nose('TipProbeContourR26',16.969,41.42,54.98)
probe=op('TipProbeFrontR26','Common',cyl('TipProbeBlankR26',1.75,94.5,2.1),smallnose)
flange=cyl('TipShoeRearFlangeR26',3.7,94.3,.2)
groove=op('TipShoeClipGrooveToolR26','Cut',cyl('TipShoeGrooveOuterR26',1.8,94.68,.68),cyl('TipShoeGrooveCoreR26',1.15,94.67,.70))
shoe=op('StationaryPickupShoeR26','Cut',fuse('TipShoeBlankR26',[probe,flange]),groove)
shoe.Placement=A.Placement(A.Vector(0,-.02,0),A.Rotation())
shoe.Label='Stationary metal pickup / .25mm PCB bond / candidate E-clip groove'
clip=op('TipClipFittedEnvelopeR26','Cut',cyl('TipClipOuterEnvelopeR26',3.2,94.70,.64),cyl('TipClipInnerEnvelopeR26',1.15,94.69,.66))
clip.Label='FITTED E-clip envelope only / DIN6799 2.3 candidate / no actual E profile'
clip.addProperty('App::PropertyString','EnvelopeScope');clip.EnvelopeScope='Conservative fitted annular envelope: OD6.4/thickness.64 allowances vs reference6.3/.6. Not exact E geometry, elastic installation or actual contact/load area.'
D.recompute();print('native tip parts recomputed',flush=True)
board=D.getObject('TipPCB')
faces=[f for f in board.Shape.Faces if f.BoundBox.YLength<1e-6 and abs(f.BoundBox.YMax-94.03)<1e-5]
assert len(faces)==1
back=D.addObject('Part::Feature','TipBackFaceR26');back.Shape=faces[0].copy()
bond=D.addObject('Part::Extrusion','TipDielectricBondR26');bond.Base=back;bond.Dir=A.Vector(0,1,0);bond.LengthFwd=.25;bond.Solid=True
bond.Label='0.25mm dielectric thermal adhesive / SE4485L candidate / cure and isolation unqualified'
currentinner=nose('CurrentTipCavityR26',17.169,41.62,54.98)
gelblank=op('TipGelBlankR26','Common',currentinner,cyl('TipGelFootprintR26',1.75,95.34,1.4))
gel=op('TipCapThermalGelR26','Cut',gelblank,shoe)
gel.Label='Cap-to-shoe gel reservation / GEL37 candidate / sliding response unqualified'
potting=box('TipStrainReliefProcessAllowanceR26',[-2.6,91.2,-5.5,2.6,92.6,-3.3])
potting.Label='Strain-relief cure volume / insulated wires only / process not yet selected'
D.recompute()

def inv(s):
 b=s.optimalBoundingBox(False,False)
 return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0
 return a.copy().common(b.copy()).Volume
parts={n:D.getObject(n)for n in r['parts']if n not in ['PortedCarrierR20','TipThermalShoe']}
parts.update({o.Name:o for o in [carrier,module,screw,shoe,clip,bond,gel]})
mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']};allowances[potting.Name]=potting
for n,o in parts.items():assert o.Shape.isValid()and len(o.Shape.Solids)==(2 if n=='TipComponentEnvelope'else 1),(n,inv(o.Shape))
changed=['PortedCarrierR20','TipPCB','TipComponentEnvelope','TipThermalShoe'];preserved={}
for n,s in old.items():
 if n in changed:continue
 a=parts[n].Shape;exact=s.exportBrepToString()==a.exportBrepToString();removed,added=(0,0)if exact else(s.copy().cut(a.copy()).Volume,a.copy().cut(s.copy()).Volume)
 assert removed<1e-4 and added<1e-4,(n,removed,added)
 preserved[n]={'removed_mm3':removed,'added_mm3':added,'exact_BRep_equal':exact}
hits=[];named=[];pairs=0
for (n,o),(m,p)in itertools.combinations(parts.items(),2):
 pairs+=1;v=vol(o.Shape,p.Shape)
 if v<1e-5:continue
 row={'a':n,'b':m,'intersection_mm3':v}
 if carrier.Name in [n,m]and(any(k.startswith('KeeperScrew')for k in [n,m])or screw.Name in [n,m]):named.append(row)
 else:hits.append(row)
matehits=[]
for n,o in mates.items():
 for m,p in parts.items():
  if m=='R17_'+n.removeprefix('R17Mate_'):continue
  v=vol(o.Shape,p.Shape)
  if v>1e-5:matehits.append({'mate':n,'fixed':m,'intersection_mm3':v})
print('static',pairs,'unexpected',hits,'mates',matehits,flush=True)
out={'builder_sha256':sha(Path(__file__)),'native_wire_library_sha256':sha(Path(__file__).with_name('tip_wire_native_r26.py')),'wire_guide_plan_sha256':sha(wireplan),'source_R25_native_sha256':r['native_sha256'],'source_R25_report_sha256':sha(SOURCE/'geometry-report.json'),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':{n:inv(o.Shape)for n,o in mates.items()},'allowances':{n:inv(o.Shape)for n,o in allowances.items()},'preserved_R25_roles':preserved,'static_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':named,'nominal_mate_intersections':matehits,'tip_geometry':{'receiver_maximum_radial_envelope_mm':15.1,'motor_mount_ring_inner_radius_mm':15.5,'minimum_radial_ring_transport_budget_mm':.4,'guide_channel_radius_mm':.45,'PCB_translation_Y_mm':-.77,'PCB_front_Y_mm':93.41,'PCB_back_Y_mm':94.03,'bond_thickness_mm':.25,'loaded_shoe_translation_Y_mm':-.02,'shoe_probe_diameter_mm':3.5,'shoe_flange_diameter_mm':7.4,'clip_groove_diameter_mm':2.3,'clip_groove_width_mm':.68,'fitted_clip_envelope_OD_mm':6.4,'fitted_clip_envelope_thickness_mm':.64,'front_gel_minimum_nominal_distance_mm':shoe.Shape.distToShape(D.getObject('MotorSeatCapR25').Shape)[0]},'scope':'Detachable stationary tip-support proposal with metal pickup, fitted E-clip envelope and thermal/process reservations. Independent of motor mount. Native PCB/circuit unchanged; tip pose moves-.77Y. No actual wires yet, true clip profile/deflection, adhesive/cure/isolation, preload/response/strength, screw thread/process, seal or physical qualification. BatteryOPEN.'}
D.Label='R26 / detachable stationary tip and individual-wire study / DEVELOPMENT';output=OUT/'StationaryTipR26.FCStd';D.saveAs(str(output));out['native_sha256']=sha(output)
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')
# Complete tip module approaches along the motor's left side, after motor seating.
module_roles=[module,shoe,clip,board,D.getObject('TipComponentEnvelope'),bond,gel,potting]
waiting={o.Name for o in module_roles}|{screw.Name,'MotorSeatCapR25'}
fixed=[o for n,o in parts.items()if n not in waiting]+list(mates.values())
motion=[]
for y in [60,40,20,10,5,2,1,.5,.25,0]:
 bad=[]
 for o in module_roles:
  if o==potting:continue
  s=o.Shape.copy();s.translate(A.Vector(0,y,0))
  for p in fixed:
   v=vol(s,p.Shape)
   if v>1e-5:bad.append({'moving':o.Name,'fixed':p.Name,'intersection_mm3':v})
 motion.append({'Y_offset_mm':y,'hits':bad});print('tip module Y',y,bad,flush=True)
out['tip_module_listed_loading_poses']=motion
capmotion=[]
for y in [20,5,1,.25,0]:
 for angle in [0,90,180,270]:
  s=D.getObject('MotorSeatCapR25').Shape.copy();s.rotate(A.Vector(0,0,0),A.Vector(0,1,0),angle);s.translate(A.Vector(0,y,0));bad=[]
  for o in module_roles+[screw]:
   v=vol(s,o.Shape)
   if v>1e-5:bad.append({'fixed':o.Name,'intersection_mm3':v})
  capmotion.append({'Y_offset_mm':y,'angle_deg':angle,'hits':bad})
out['cap_to_tip_listed_poses']=capmotion;print('cap hits',[x for x in capmotion if x['hits']],flush=True)
meshes={};side=Part.makeBox(100,250,100,A.Vector(-100,-100,-50))
for n,o in dict(parts,**mates,**allowances).items():
 for suffix,s in [('',o.Shape)]+([('-side-section',o.Shape.copy().common(side.copy()))]if n in ['KeyedBodyR25','MotorSeatCapR25','ShellMotorMountR25',module.Name]else[]):
  if s.Volume<1e-6:continue
  f=OUT/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
out['review_meshes_sha256']=meshes;(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==r['native_sha256'];print('saved',output,flush=True)
