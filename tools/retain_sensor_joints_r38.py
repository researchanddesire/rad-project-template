"""One removable comb and screw for the four NTC laps and return junction."""
from pathlib import Path
import hashlib,itertools,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-assembly-r37/power-f';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());source=P/'ConditionalPackPowerR37.FCStd';before=sha(source);assert before==r['native_sha256'];D=A.openDocument(str(source))
def feature(n,s,label=None):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n;return o
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def cyl(n,radius,L,point,axis):
 o=D.addObject('Part::Cylinder',n);o.Radius=radius;o.Height=L;o.Placement=A.Placement(A.Vector(*point),A.Rotation(A.Vector(0,0,1),A.Vector(*axis)));return o
def fuse(n,items):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=items;o.Refine=True;return o
def cut(n,base,tool):
 o=D.addObject('Part::Cut',n);o.Base=base;o.Tool=tool;o.Refine=True;return o
def volume(s):return 0. if s.isNull()else s.Volume
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return volume(a.copy().common(b.copy()))
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
base=D.getObject('PoweredServiceablePackHubR36');pocket=box('JointCombHubPocketR38',[16.8,-14.63,-5.7,22.8,-10.7,8.7]);relieved=cut('JointCombRelievedHubR38',base,pocket);post=cyl('JointCombPostR38',1.7,3.35,[19.8,-15.45,7.0],[0,1,0]);pilot=cyl('JointCombPilotR38',.625,3.6,[19.8,-15.5,7.0],[0,1,0]);slot=box('JointCombKeySlotR38',[17.4,-15.5,-6.6,19.,-14.1,-5.6]);hub=cut('JointRetainingHubR38',fuse('JointRetainingHubBlankR38',[relieved,post]),fuse('JointCombHubHolesR38',[pilot,slot]))
bits=[box('JointCombMainR38',[17.,-14.43,-5.5,22.6,-10.9,8.5]),box('JointCombUprightR38',[19.,-14.2,7.9,20.6,-11.6,14.6]),box('JointCombBridgeR38',[11.,-14.2,13.6,20.6,-13.,14.6]),box('JointCombKeyFootR38',[17.2,-14.43,-6.9,19.2,-12.5,-5.1]),box('JointCombKeyR38',[17.5,-15.2,-6.5,18.9,-14.2,-5.7])]
plug=box('ReturnJointDropInPlugR38',[10.2,-14.2,.65,13.,-13.,13.6]);plug.Label='Separate top-loaded return plunger / captured by removable comb bridge'
tools=[cyl('JointCombPostPocketR38',1.8,3.4,[19.8,-15.5,7.0],[0,1,0]),cyl('JointCombScrewHoleR38',.9,1.5,[19.8,-12.2,7.0],[0,1,0])];pads=[];targets=[]
halfspace=Part.makeBox(20,20,40,A.Vector(10,-14.43,-20))
for key,z in [('1_1',-1.85),('1_2',-4.15),('2_1',4.15),('2_2',1.85)]:
 tools +=[cyl('JointCombSeatR38_'+key,1.1,5.1,[17.25,-14.43,z],[1,0,0]),cyl('JointCombWireThroatR38_'+key,.8,6.,[16.8,-14.43,z],[1,0,0])]
 outer=Part.makeCylinder(1.1,4.6,A.Vector(17.5,-14.43,z),A.Vector(1,0,0));inner=Part.makeCylinder(.9,4.8,A.Vector(17.4,-14.43,z),A.Vector(1,0,0));shape=outer.cut(inner).common(halfspace.copy());pad=feature('JointCombSoftPadR38_'+key,shape,'0.20 radial compliant-pad target / actual material and preload OPEN');pads.append(pad);targets.append(('NTCSpliceSpaceR36_'+key,pad.Name))
pad=box('ReturnJointSoftPadR38',[10.2,-14.2,.45,13.,-13.,.65]);pad.Label='Return-joint top contact soft-pad target / no qualified preload';pads.append(pad);targets.append(('SensorReturnYJointR36',pad.Name))
comb=cut('SensorJointCombR38',fuse('JointCombBlankR38',bits),fuse('JointCombCutToolsR38',tools));comb.Label='One removable sensor-joint comb / four lap end stops + return plunger'
screw=fuse('JointCombScrewEnvelopeR38',[cyl('JointCombShankR38',.8,4.,[19.8,-14.9,7.],[0,1,0]),cyl('JointCombHeadR38',1.6,1.6,[19.8,-10.9,7.],[0,1,0])]);screw.Label='M1.6x4 candidate screw envelope / actual pilot, material and torque OPEN'
D.recompute();assert hub.Shape.isValid()and len(hub.Shape.Solids)==1;assert comb.Shape.isValid()and len(comb.Shape.Solids)==1
physical={n:D.getObject(n).Shape.copy()for n in r['fixed_roles']+list(r['new_roles'])if n!=base.Name};new={o.Name:o.Shape.copy()for o in [hub,comb,plug,screw]+pads};hits=[];known=[];count=0
for n,s in new.items():
 for m,t in physical.items():
  count+=1;v=overlap(s,t)
  if v<=1e-5:continue
  inherited=overlap(base.Shape,t)if n==hub.Name else 0.
  added_overlap=volume(s.copy().common(t.copy()).cut(base.Shape.copy()))if n==hub.Name else v
  row={'a':n,'b':m,'intersection_mm3':v,'source_overlap_mm3':inherited,'added_overlap_mm3':added_overlap}
  (known if n==hub.Name and added_overlap<1e-5 and inherited>1e-5 else hits).append(row)
 print('static',n,'hits so far',hits,flush=True)
for(a,s),(b,t)in itertools.combinations(new.items(),2):
 count+=1;v=overlap(s,t)
 if v<=1e-5:continue
 row={'a':a,'b':b,'intersection_mm3':v};(known if {a,b}=={hub.Name,screw.Name}else hits).append(row)
contacts=[]
for target,padname in targets:
 s=D.getObject(target).Shape.copy();p=D.getObject(padname).Shape.copy();contacts.append({'joint':target,'pad':padname,'nominal_gap_mm':s.distToShape(p)[0],'intersection_mm3':overlap(s,p)})
out=OUT/'RetainedSensorJointsR38.FCStd';D.Label='R38 shared sensor-joint comb / DEVELOPMENT / battery OPEN';D.saveAs(str(out));report={'native_sha256':sha(out),'source_R37F_sha256':before,'builder_sha256':sha(Path(__file__)),'new_roles':{n:inv(s)for n,s in new.items()},'fixed_roles':list(physical),'replaced_hub':base.Name,'static_pairs':count,'unexpected_intersections':hits,'named_inherited_or_screw_interfaces':known,'nominal_joint_pad_contacts':contacts,'all_static_screens_clear':not hits,'scope':'Shared four-lap/return-junction comb, one candidate M1.6x4 screw, integral post and compliant-pad targets. No actual material, preload, pilot/torque, tool/loading, joint/pad creep, strength or physical acceptance. Pack power connector/laps still unrestrained; battery OPEN and product BOM unchanged.'};(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('SAVED shared comb clear',not hits,'contacts',contacts,flush=True)
