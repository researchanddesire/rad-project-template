"""Conditional local split connector cradle; one lid screw and locating key."""
from pathlib import Path
import hashlib,itertools,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/power-retention-r39/power-r';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());source=P/'ForwardPackPowerR39.FCStd';before=sha(source);assert before==r['native_sha256'];D=A.openDocument(str(source))
def feature(n,s,label=None):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n;return o
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def fuse(n,items):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=items;o.Refine=True;return o
def cut(n,base,tool):
 o=D.addObject('Part::Cut',n);o.Base=base;o.Tool=tool;o.Refine=True;return o
def rotated_box(x0,x1,width,thick):
 s=Part.makeBox(x1-x0,width,thick,A.Vector(x0,-width/2,-thick/2));s.rotate(A.Vector(),A.Vector(1,0,0),20.);s.translate(A.Vector(0,-9.5,-11.5));return s
def vol(s):return 0. if s.isNull()else s.Volume
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return vol(a.copy().common(b.copy()))
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
rotation=A.Rotation(A.Vector(1,0,0),20.);centre=A.Vector(0,-9.5,-11.5);n=rotation.multVec(A.Vector(0,1,0));taxis=rotation.multVec(A.Vector(0,0,1))
def local_box(name,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',name);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement=A.Placement(centre+rotation.multVec(A.Vector(x,y,z)),rotation);return o
def local_cyl(name,radius,L,point):
 o=D.addObject('Part::Cylinder',name);o.Radius=radius;o.Height=L;o.Placement=A.Placement(centre+rotation.multVec(A.Vector(*point)),rotation);return o
def chain(name,items):
 current=items[0]
 for i,item in enumerate(items[1:],1):
  o=D.addObject('Part::Fuse',name if i==len(items)-1 else name+'Step'+str(i));o.Base=current;o.Tool=item;o.Refine=True;current=o
 return current
male=r['conditional_case']['male_housing_back_X_mm'];stock=r['conditional_case']['stock_female_back_X_mm']
outer_box=feature('MateCradleOuterBoxR39',rotated_box(male-1.6,stock+4.8,10.4,5.8));rounded=outer_box.Shape.copy();outer=feature('MateCradleOuterR39',rounded.makeFillet(.6,rounded.Edges),'R0.60 outer edges; nominal0.60 side/bottom wall')
main=local_box('MateMainLoadingWindowR39',[male-1.,-4.6,-2.3,stock+1.,4.6,6.9]);tail=local_box('MateShrinkLoadingWindowR39',[stock+.8,-3.4,-2.3,stock+4.2,3.4,6.9]);male_slot=local_box('MateMaleWireLoadingSlotR39',[male-1.8,-2.2,-.05,male+.2,2.2,6.9]);stock_slot=local_box('MateStockWireLoadingSlotR39',[stock+.8,-2.2,-.05,stock+5.,2.2,6.9]);channels=[D.getObject(p+str(i))for p in ['StockPackLeadChannelR39_','SpareMateChannelR39_']for i in [1,2]]
load_tools=fuse('MateBodyAndWireLoadingToolsR39',[main,tail,male_slot,stock_slot]+channels)
lower=local_box('MateCupLowerHalfspaceR39',[-60,-30,-30,0,30,2.3]);upper=local_box('MateLidUpperHalfspaceR39',[-60,-30,2.3,0,30,30]);D.recompute();cup=feature('MateOpenTopCupR39',outer.Shape.copy().common(lower.Shape.copy()),'Open top cup; body and wire entry windows cut after union');roof=feature('MateFlatRoofR39',outer.Shape.copy().common(upper.Shape.copy()),'Flat roof; no trapped wire hoops')
base=D.getObject('ForwardWirePoweredConnectedPackTailLeftHubR34');roof_clear=local_box('MateFlatLidTravelClearanceR39',[male-1.8,-8.7,2.1,stock+5.,27.5,3.4]);tab_clear=local_box('MateFlatLidTabTravelClearanceR39',[-28.3,-8.7,2.1,-23.7,27.5,3.8]);prepared=cut('MateLidRelievedSourceHubR39',base,fuse('MateLidSourceClearanceToolsR39',[roof_clear,tab_clear]))
supports=[box('MateCupGlobalSupportR39_'+str(i),[x-.8,-17.2,-13.5,x+.8,-14.6,-8.2])for i,x in enumerate([-29.,-17.],1)]
post=local_cyl('MateLidPostR39',1.7,3.5,[-26.,-6.4,-1.2]);pilot=local_cyl('MateLidPilotR39',.625,3.7,[-26.,-6.4,-1.3]);boss=local_box('MateLidKeyBossR39',[-32.9,-7.4,-1.2,-31.1,-4.9,2.3]);key=local_box('MateLidFixedKeyR39',[-32.5,-6.9,2.2,-31.5,-5.9,2.5]);blank=chain('MateHubBlankR39',[prepared]+supports+[cup,post,boss,key]);hub=cut('RetainedPackMateLeftHubR39',blank,fuse('MateHubToolsR39',[load_tools,pilot]));hub.Label='Open-top mate cup, mounting supports and local lid post'
tab=local_box('MateLidScrewTabR39',[-28.1,-8.5,2.3,-23.9,-4.3,3.3]);keytab=local_box('MateLidKeyTabR39',[-32.7,-7.4,2.3,-31.3,-4.9,2.9]);hole=local_cyl('MateLidScrewHoleR39',.9,1.3,[-26.,-6.4,2.2]);keyhole=local_box('MateLidKeyHoleR39',[-32.6,-7.0,2.2,-31.4,-5.8,3.1]);notches=[local_box('MateLidSupportNotchR39_'+str(i),[x-1.,-8.7,2.2,x+1.,-4.4,3.1])for i,x in enumerate([-29.,-17.],1)];cap=cut('PackMateLidR39',chain('MateLidBlankR39',[roof,tab,keytab]),fuse('MateLidToolsR39',[hole,keyhole]+notches));cap.Label='Flat mate lid, shallow locating key and one M1.6x4 candidate screw'
screw=fuse('MateLidScrewEnvelopeR39',[local_cyl('MateLidShankR39',.8,4.,[-26.,-6.4,-.7]),local_cyl('MateLidHeadR39',1.6,1.6,[-26.,-6.4,3.3])]);D.recompute();physical={name:D.getObject(name).Shape.copy()for name in r['fixed_roles']+list(r['new_roles'])if name!=base.Name};new={o.Name:o.Shape.copy()for o in [hub,cap,screw]};hits=[];known=[];pairs=0
for name,s in new.items():
 assert s.isValid()and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
 for other,q in physical.items():
  pairs+=1;value=overlap(s,q)
  if value<=1e-5:continue
  old=overlap(base.Shape,q)if name==hub.Name else 0.;added=vol(s.copy().common(q.copy()).cut(base.Shape.copy()))if name==hub.Name else value;row={'a':name,'b':other,'intersection_mm3':value,'source_intersection_mm3':old,'new_material_intersection_mm3':added};(known if old>1e-5 and added<1e-5 else hits).append(row)
 print('static',name,hits,flush=True)
for(a,s),(b,q)in itertools.combinations(new.items(),2):
 pairs+=1;value=overlap(s,q)
 if value>1e-5:
  row={'a':a,'b':b,'intersection_mm3':value};(known if {a,b}=={hub.Name,screw.Name}else hits).append(row)
out=OUT/'PackMateCradleR39.FCStd';D.Label='R39 open-top conditional mate cup / flat lid / battery OPEN';D.saveAs(str(out));result={'native_sha256':sha(out),'source_R39_power_R_sha256':before,'builder_sha256':sha(Path(__file__)),'new_roles':{name:inv(s)for name,s in new.items()},'fixed_roles':list(physical),'replaced_roles':[base.Name],'static_pairs':pairs,'unexpected_intersections':hits,'inherited_or_candidate_pilot_interfaces':known,'new_single_solids':True,'all_static_screens_clear':not hits,'local_frame':{'centre_xyz_mm':list(centre),'rotation_X_degrees':20.,'lid_lift_axis_xyz':list(taxis),'lid_front_axis_xyz':list(n),'lid_lift_T_mm':.3,'lid_front_travel_W_mm':21.,'nominal_wall_mm':.6,'outside_edge_radius_mm':.6,'screw_centre_local_XW_mm':[-26.,-6.4],'screw_head_front_T_mm':4.9},'scope':'Open-top mate cup with open wire-entry slots and flat local lid. Requires24mm usable flexible pack lead; the old35mm reference cable is not accepted as a routing match. One local screw, independent of the separate power-lap comb screw. Body/wire topology/exterior/motor/sensor retainer unchanged; battery OPEN/BOM unchanged. Loading, actual mating retention/preload/current/strength and physical fit remain to qualify.'};(OUT/'geometry-report.json').write_text(json.dumps(result,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('SAVED open cup clear',not hits,flush=True)
