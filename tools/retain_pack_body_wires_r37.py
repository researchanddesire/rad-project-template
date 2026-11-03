"""R37: under-board pack-wire saddle on unused tray; one cable tie, no new screw.

Installed tie/head shapes are engineering bounds tied to the Panduit reference,
not qualified clamp pressure or supplier maximum formed geometry.
"""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/cad/pack-sensor-r36/access-i';H=ROOT/'hardware/cad/pack-sensor-r36/connected-h';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((SOURCE/'access-review.json').read_text());h=json.loads((H/'geometry-report.json').read_text());source=SOURCE/'ServiceablePackSensorsR36.FCStd';before=sha(source);assert before==r['native_sha256'];D=A.openDocument(str(source))
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def feature(n,s,label):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label;return o
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
base=D.getObject('PackWireCarrierR34')
saddle=box('PackWireSaddleBlankR37',[-4.95,33.5,-10.8,1.95,38.5,-5.7])
blank=D.addObject('Part::MultiFuse','PackWireCarrierBlankR37');blank.Shapes=[base,saddle];blank.Refine=True
band_channel=box('PackTieChannelR37',[-6.4,34.7,-8.1,3.7,37.3,-6.55])
head_access=box('PackTieHeadAccessR37',[-9.8,33.5,-12.,-5.1,38.5,-8.3])
tools=D.addObject('Part::MultiFuse','PackAnchorCutToolsR37');tools.Shapes=[band_channel,head_access];tools.Refine=True
carrier=D.addObject('Part::Cut','PackAnchoredCarrierR37');carrier.Base=blank;carrier.Tool=tools;carrier.Refine=True;D.recompute();assert carrier.Shape.isValid()and len(carrier.Shape.Solids)==len(base.Shape.Solids)
pad=box('PackWireSoftPadR37',[-4.8,34.8,-5.7,1.8,37.2,-5.5]);pad.Label='0.20mm compliant-pad process target / no adhesive load-path assumption'

def rounded_xz(bounds,rad,y0,depth):
 x,z,u,w=bounds
 shapes=[Part.makeBox(u-x-2*rad,depth,w-z,A.Vector(x+rad,y0,z)),Part.makeBox(u-x,depth,w-z-2*rad,A.Vector(x,y0,z+rad))]
 for cx in [x+rad,u-rad]:
  for cz in [z+rad,w-rad]:shapes.append(Part.makeCylinder(rad,depth,A.Vector(cx,y0,cz),A.Vector(0,1,0)))
 return shapes[0].multiFuse(shapes[1:]).removeSplitter()
outer=rounded_xz([-6.3,-7.9,3.5,-3.8],1.95,34.9,2.2)
inner=rounded_xz([-5.2,-6.8,2.4,-4.9],.85,34.8,2.4)
band_shape=outer.cut(inner).removeSplitter();assert band_shape.isValid()and len(band_shape.Solids)==1
band=feature('PackTieBandSpaceR37',band_shape,'Installed band2.2wide/1.1thick allowance / not received formed tie')
head=box('PackTieHeadSpaceR37',[-9.6,33.9,-9.9,-5.3,38.1,-5.7]);head.Label='Conservative4.3x4.2x4.2 head/process allowance; check actual geometry/orientation'
tie=D.addObject('Part::MultiFuse','PackTieSpaceR37');tie.Shapes=[band,head];tie.Refine=True;D.recompute();assert tie.Shape.isValid()and len(tie.Shape.Solids)==1

protected={}
for name,s in [('TipReceiverR26',D.getObject('TipReceiverR26').Shape.copy()),('SupportedWireCombR26',D.getObject('SupportedWireCombR26').Shape.copy()),('rear_capture_Y_below26',base.Shape.copy().common(Part.makeBox(100,66,100,A.Vector(-50,-40,-50)))),('PCB_guides_Z_above_minus1_2',base.Shape.copy().common(Part.makeBox(100,100,51.2,A.Vector(-50,-20,-1.2))))]:
 loss=s.copy().cut(carrier.Shape.copy()).Volume;assert abs(loss)<1e-5,(name,loss);protected[name]={'source_volume_mm3':s.Volume,'lost_mm3':loss}
physical={n:D.getObject(n).Shape.copy()for n in h['fixed_roles']+h['new_roles']if n not in ['ConnectedSensorWiredRightHubR36','PackWireCarrierR34']};physical['ServiceablePackHubR36']=D.getObject('ServiceablePackHubR36').Shape.copy();new={carrier.Name:carrier.Shape.copy(),pad.Name:pad.Shape.copy(),tie.Name:tie.Shape.copy()};hits=[];inherited=[];pairs=0
for n,s in new.items():
 local=[]
 for m,a in physical.items():
  pairs+=1;v=vol(s,a)
  if v>1e-5:
   oldv=vol(base.Shape.copy(),a)if n==carrier.Name else 0.
   added_overlap=s.copy().common(a.copy()).cut(base.Shape.copy()).Volume if n==carrier.Name else v
   row={'new':n,'fixed':m,'intersection_mm3':v,'source_carrier_intersection_mm3':oldv,'added_intersection_mm3':added_overlap}
   (inherited if n==carrier.Name and added_overlap<1e-5 and oldv>1e-5 else local).append(row)
 hits+=local;print('static',n,local,flush=True)
names=list(new)
for i,n in enumerate(names):
 for m in names[i+1:]:
  pairs+=1;v=vol(new[n],new[m])
  if v>1e-5:hits.append({'a':n,'b':m,'intersection_mm3':v})
# Axial tie restraint comes from the two guide faces, independently of pad
# adhesion. This tests bounded finite motion of the formed allowance only.
blockers=[]
for sign in [-1,1]:
 first=None
 for step in range(1,11):
  distance=step*.05;moving=tie.Shape.copy();moving.translate(A.Vector(0,sign*distance,0));v=vol(moving,carrier.Shape.copy())
  if v>1e-5:first={'distance_mm':distance,'intersection_mm3':v};break
 blockers.append({'direction_Y':sign,'first_sampled_carrier_blocker':first})
out=OUT/'PackBodyAnchorR37.FCStd';D.Label='R37 under-board pack-wire saddle / no new screw / DEVELOPMENT';D.saveAs(str(out));result={'native_sha256':sha(out),'source_R36I_sha256':before,'builder_sha256':sha(Path(__file__)),'new_roles':{n:inv(s)for n,s in new.items()},'fixed_roles':list(physical),'protected_source_material':protected,'carrier_added_mm3':carrier.Shape.copy().cut(base.Shape.copy()).Volume,'carrier_removed_mm3':base.Shape.copy().cut(carrier.Shape.copy()).Volume,'static_pairs':pairs,'unexpected_intersections':hits,'inherited_source_fastener_interfaces':inherited,'axial_tie_blocker_probes':blockers,'all_static_screens_clear':not hits,'tie_reference':{'part':'PanduitPLT.6SM-C','manufacturer_drawing':'SS-5540sheet1rev36A','strap_nominal_thickness_mm':.76,'strap_nominal_width_mm':1.8,'strap_explicit_tolerance_mm':.25,'reserved_band_width_mm':2.2,'reserved_band_thickness_mm':1.1,'head_reserved_xyz_mm':[4.3,4.2,4.2],'minimum_catalog_bundle_diameter_mm':1.6,'model_inside_corner_radius_mm':.85},'scope':'New carrier saddle/pad and formed tie/head engineering allowances around the unchanged five-wire fan. Pad and band touch nominal wire bounds; actual formed geometry, tie tension, jacket/pad behavior and pull/creep/vibration loads unqualified. Guide-face finite blockers are not clamp-force proof. Source fastener intersections are retained separately only after exact proof that no added carrier material enters them. No motor-to-PCB coupling, board/wire pose change, extra screw or battery adoption. Body loading/tool access, power mate, flange joint keeper and full prototype remain unfinished.'};(OUT/'geometry-report.json').write_text(json.dumps(result,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('SAVED body anchor clear',result['all_static_screens_clear'],'blockers',blockers,flush=True)
