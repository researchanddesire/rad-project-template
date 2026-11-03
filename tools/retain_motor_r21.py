"""R21 conditional motor cage, preserving the R20D body and native PCB poses.

The drawing fixes capsule and lead-flare axial lengths, but not the flare's
radial maximum. The cone is a declared design allowance, not supplier geometry.
"""
from pathlib import Path
import sys, json, hashlib, itertools
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part, MeshPart

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
SOURCE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert not any(OUT.iterdir()), 'Preserve executed candidates'
nf = SOURCE / 'PCBIntegrationR20.FCStd'
rp = SOURCE / 'geometry-report.json'
r = json.loads(rp.read_text())
assert sha(nf) == r['native_sha256']
D = A.openDocument(str(nf))
old = {n: D.getObject(n).Shape.copy() for n in r['parts']}

def box(n, bb):
    x, y, z, u, v, w = bb
    o = D.addObject('Part::Box', n)
    o.Length, o.Width, o.Height = u-x, v-y, w-z
    o.Placement.Base = A.Vector(x, y, z)
    return o

def cyl(n, radius, y, length):
    o = D.addObject('Part::Cylinder', n)
    o.Radius, o.Height = radius, length
    o.Placement = A.Placement(A.Vector(0, y, 3.5), A.Rotation(A.Vector(0,0,1), A.Vector(0,1,0)))
    return o

def op(n, t, a, b):
    o = D.addObject('Part::'+t, n)
    o.Base, o.Tool, o.Refine = a, b, True
    return o

def fuse(n, objects):
    o = D.addObject('Part::MultiFuse', n)
    o.Shapes, o.Refine = objects, True
    return o

# Translate primitives, not just the final carrier snapshot. The lower
# saddles and support remain editable dependencies of the existing carrier.
shifted = []
for o in D.Objects:
    if o.Name.startswith(('MotorSaddleOuter', 'MotorSaddleInner', 'LowerSaddleHalf')) or o.Name in ['MotorSupportStem', 'TrayToMotorBridge', 'MotorMaxEnvelope']:
        v = o.Placement.Base
        o.Placement.Base = A.Vector(v.x, v.y+6.5, v.z)
        shifted.append(o.Name)

# The same keeper supports two upper half-hoops and both axial stops.
# Lower halves remain on the carrier. Feet avoid the two screw-head budgets.
slots=[]
for ref in ['J3','J5']:
    a,b,z,c,e,w=r['port_cut_bounds_xyz_mm'][ref]
    slots.append(box('KeeperOpenBottomPortR21_'+ref,[a,b,-1.6,c,e,4.0]))
open_keeper=op('OpenBottomKeeperR21','Cut',D.getObject('PortedKeeperR20'),fuse('KeeperOpenBottomPortToolsR21',slots))
members = [open_keeper,
    box('KeeperUpperPlugBridgeR21',[-7.4,54.1,4.1,7.4,54.8,4.8]),
    box('KeeperCentralPlugBridgeR21',[-2.4,54.1,.6,.3,54.8,4.8])]
for sign in [-1, 1]:
    x0, x1 = (6.4, 7.4) if sign > 0 else (-7.4, -6.4)
    members.append(box('MotorKeeperFootR21'+str(sign), [x0,54.1,.6,x1,55.1,4.8]))
    members.append(box('MotorKeeperSpineR21'+str(sign), [x0,54.1,3.5,x1,89,4.8]))
for y in [63, 85]:
    ring = op('UpperMotorRingR21_'+str(y), 'Cut', cyl('UpperMotorOuterR21_'+str(y), 6.75,y,2), cyl('UpperMotorInnerR21_'+str(y),5.75,y-.1,2.2))
    members.append(op('UpperMotorHoopR21_'+str(y),'Common',ring,box('UpperMotorHalfR21_'+str(y),[-10,y-.2,3.5,10,y+2.2,15])))
rear = op('RearMotorStopRingR21','Cut',cyl('RearMotorStopOuterR21',6.75,61.4,.6),cyl('RearMotorLeadOpeningR21',5.0,61.3,.8))
members.append(op('RearMotorStopR21','Common',rear,box('RearMotorStopHalfR21',[-10,61.3,3.5,10,62.1,15])))
front = cyl('FrontMotorStopBlankR21',5.75,88.5,.5)
members.append(op('FrontMotorStopR21','Common',front,box('FrontMotorStopHalfR21',[-10,88.4,3.5,10,89.1,15])))
members.append(box('FrontMotorStopTieR21',[-7.4,88.5,3.5,7.4,89,4.8]))
keeper = fuse('MotorKeeperR21', members)
keeper.Label = 'One keeper / PCB and motor cage / same two screws / conditional lead flare'

flare = D.addObject('Part::Cone','MotorLeadFlareAllowanceR21')
flare.Radius1, flare.Radius2, flare.Height = .9, 4.8, 6.2
flare.Placement = A.Placement(A.Vector(0,55.8,3.5), A.Rotation(A.Vector(0,0,1), A.Vector(0,1,0)))
flare.addProperty('App::PropertyString','Scope')
flare.Scope = '6 mm MAX axial flare from drawing plus .2 mm design margin; .9/4.8 mm radii are inferred allowance, NOT controlled maker maxima.'
parts = {n:D.getObject(n) for n in r['parts'] if n != 'PortedKeeperR20'}
parts[keeper.Name] = keeper
mates = {n:D.getObject(n) for n in r['mates']}
D.recompute()

def inv(s):
    b = s.optimalBoundingBox(False,False)
    return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}

def volume(a,b):
    aa,bb=a.BoundBox,b.BoundBox
    if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max')) <= max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in 'XYZ'):return 0
    return a.copy().common(b.copy()).Volume

assert len(keeper.Shape.Solids)==1 and keeper.Shape.isValid(), inv(keeper.Shape)
assert len(D.getObject('PortedCarrierR20').Shape.Solids)==1
changed={'MotorMaxEnvelope','PortedCarrierR20','PortedKeeperR20'}
conservation={}
for n,s in old.items():
    if n in changed:continue
    a=D.getObject(n).Shape
    exact_brep_equal=s.exportBrepToString()==a.exportBrepToString()
    removed,added=(0,0) if exact_brep_equal else (s.cut(a).Volume,a.cut(s).Volume)
    assert removed<1e-4 and added<1e-4,(n,removed,added)
    conservation[n]={'removed_mm3':removed,'added_mm3':added,'exact_BRep_equal':exact_brep_equal}
hits=[]; named=[]; pairs=0
for (n,o),(m,p) in itertools.combinations(parts.items(),2):
    pairs+=1;v=volume(o.Shape,p.Shape)
    if v<1e-5:continue
    q={'a':n,'b':m,'intersection_mm3':v}
    if 'PortedCarrierR20' in [n,m] and any(k.startswith('KeeperScrew') for k in [n,m]):named.append(q)
    else:hits.append(q)
matehits=[]
for n,o in mates.items():
    for m,p in parts.items():
        if m=='R17_'+n.removeprefix('R17Mate_'):continue
        v=volume(o.Shape,p.Shape)
        if v>1e-5:matehits.append({'mate':n,'target':m,'intersection_mm3':v})
flarehits=[]
for n,o in dict(parts,**mates).items():
    if n=='MotorMaxEnvelope':continue
    v=volume(flare.Shape,o.Shape)
    if v>1e-5:flarehits.append({'target':n,'intersection_mm3':v})
print('static',pairs,'hits',hits,'mates',matehits,'flare',flarehits,flush=True)
body=[D.getObject(n) for n in r['cartridge_roles'] if n.startswith('R17_') or n=='BodyPCB_R17']
carrier=D.getObject('PortedCarrierR20');motor=D.getObject('MotorMaxEnvelope');pack=D.getObject('NarrowPackAllowance')
lowering=[]
for z in [12,8,4,2,1,.5,.25,0]:
    s=keeper.Shape.copy();s.translate(A.Vector(0,0,z));bad=[]
    for o in [carrier,motor,pack,flare]+body+list(mates.values()):
        v=volume(s,o.Shape)
        if v>1e-5:bad.append({'target':o.Name,'intersection_mm3':v})
    lowering.append({'Z_offset_mm':z,'hits':bad})
    print('keeper Z',z,bad,flush=True)
moving=[D.getObject(n) if n!='PortedKeeperR20' else keeper for n in r['cartridge_roles']]+[flare]
loading=[]
for y in range(100,-1,-5):
    bad=[]
    for o in moving:
        s=o.Shape.copy();s.translate(A.Vector(0,y,0));v=volume(s,D.getObject('KeyedOnePieceBody').Shape)
        if v>1e-5:bad.append({'role':o.Name,'body_hit_mm3':v})
    loading.append({'Y_offset_mm':y,'hits':bad})
    print('cartridge Y',y,bad,flush=True)
for o in D.Objects:
    if o.ViewObject:o.ViewObject.Visibility=False
for o in list(parts.values())+[flare]:
    if o.ViewObject:o.ViewObject.Visibility=True
for n in ['FlangeCoverUpper','ServiceCoverReference']:
    if D.getObject(n).ViewObject:D.getObject(n).ViewObject.Visibility=False
D.Label='R21 / one motor and PCB keeper / conditional flare / DEVELOPMENT'
outnative=OUT/'MotorRetentionR21.FCStd'
D.recompute();D.saveAs(str(outnative))
meshes={}
section=Part.makeBox(200,250,100,A.Vector(-100,-100,-100))
for n,o in dict(parts,**mates,**{flare.Name:flare}).items():
    for suffix,s in [('',o.Shape)]+([('-section',o.Shape.copy().common(section.copy()))] if n in ['KeyedOnePieceBody','FullerClosingCap'] else []):
        if s.Volume<1e-6:continue
        f=OUT/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
out={'date':'2026-11-01','builder_sha256':sha(Path(__file__)),'source_R20_native_sha256':sha(nf),'source_R20_report_sha256':sha(rp),'native_sha256':sha(outnative),'parts':{n:inv(o.Shape) for n,o in parts.items()},'mates':{n:inv(o.Shape) for n,o in mates.items()},'allowances':{flare.Name:inv(flare.Shape)},'changed_roles':sorted(changed),'shifted_history_features':shifted,'retained_R20_material_comparison':conservation,'static_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':named,'nominal_mate_intersections':matehits,'conditional_flare_intersections':flarehits,'keeper_lowering_listed_poses':lowering,'cartridge_listed_poses':loading,'cartridge_roles':[o.Name for o in moving],'review_meshes_sha256':meshes,'motor_dimensions_mm':{'capsule_diameter_max':11.1,'capsule_length_max':26.3,'capsule_start_Y':62,'capsule_end_Y':88.3,'maker_flare_length_max':6,'allowance_flare_length':6.2,'inferred_flare_radius_near_leads':.9,'inferred_flare_radius_at_capsule':4.8,'radial_gap_before_liner':.2,'axial_gap_after_max_capsule':.2},'keeper_loading_revision':'Open-bottom J3/J5 slots with upper/central bridge; mates installed before keeper lowers', 'scope':'Conditional motor capture proposal. Maker PDF confirms capsule and axial flare, not radial flare, wire OD/bend, liner, controlled mates or load. Same two keeper screws. Exterior/15 mm neck and PCB poses preserved. Battery OPEN; no build release.'}
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name)
assert sha(nf)==r['native_sha256']
print(json.dumps({'unexpected':hits,'mates':matehits,'conditional_flare':flarehits,'keeper_clear':all(not q['hits'] for q in lowering),'cartridge_clear':all(not q['hits'] for q in loading),'native':str(outnative)},indent=2),flush=True)
