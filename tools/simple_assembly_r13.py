"""Native R13: fuller convex nose, drop-in PCB and a single U-shaped keeper.

Preserve all prior candidates. Actual R12 board poses, component Fab/height
envelopes and nominal mates are imported for review, not manufacturer models.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher,MeshPart
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args();OUT=args.directory.resolve();OUT.mkdir(parents=True,exist_ok=True)
nf=OUT/'SimpleAssemblyR13.FCStd';assert not nf.exists(),'Preserve executed CAD candidates'
R11=ROOT/'hardware/cad/front-load-retention-r11/candidate-c';src=R11/'FrontLoadRetentionR11.FCStd'
R10=ROOT/'hardware/cad/front-load-r10/candidate-c/FrontLoadR10.FCStd'
PCB=ROOT/'hardware/pcb/split-r12/candidate-i'
report=json.loads((R11/'geometry-report.json').read_text());before=sha(src);assert before==report['native_sha256']
assert sha(R10)=='b77ac8e14adba236f2824a9ad762ef02373632114d694178f8db3f3011430841'
D=A.openDocument(str(src));old={n:D.getObject(n).Shape.copy()for n in report['parts']}
def op(n,t,a,b):
    o=D.addObject('Part::'+t,n);o.Base=a;o.Tool=b;o.Refine=True;return o
def fuse(n,parts):
    o=D.addObject('Part::MultiFuse',n);o.Shapes=parts;o.Refine=True;return o
def box(n,bb):
    x,y,z,x1,y1,z1=bb;o=D.addObject('Part::Box',n);o.Length=x1-x;o.Width=y1-y;o.Height=z1-z;o.Placement.Base=A.Vector(x,y,z);return o
def snapshot(n,s):
    o=D.addObject('Part::Feature',n);o.Shape=s.copy();return o
def polygon(n,pts,z,h):
    sk=D.addObject('Sketcher::SketchObject',n+'Outline');sk.Placement.Base.z=z
    for a,b in zip(pts,pts[1:]+pts[:1]):sk.addGeometry(Part.LineSegment(A.Vector(*a,0),A.Vector(*b,0)),False)
    o=D.addObject('Part::Extrusion',n);o.Base=sk;o.Dir=A.Vector(0,0,1);o.LengthFwd=h;o.Solid=True;return o
def nose(n,radius,axial):
    cy=54.88;sk=D.addObject('Sketcher::SketchObject',n+'Meridian')
    ellipse=Part.Ellipse(A.Vector(0,cy+axial,0),A.Vector(radius,cy,0),A.Vector(0,cy,0))
    arc=Part.ArcOfEllipse(ellipse,0,math.pi/2)
    sk.addGeometry(arc,False)
    sk.addGeometry(Part.LineSegment(arc.EndPoint,A.Vector(0,cy,0)),False)
    sk.addGeometry(Part.LineSegment(A.Vector(0,cy,0),arc.StartPoint),False)
    o=D.addObject('Part::Revolution',n);o.Source=sk;o.Axis=A.Vector(0,1,0);o.Angle=360;o.Solid=True
    o.addProperty('App::PropertyString','Scope');o.Scope='True quarter-ellipse meridian; study axes, not accepted material/finish/wall/comfort.'
    return o

# User removed the requirement for the inward scoop. Change the cap's nose
# beyond the existing maximum station; retain the body/neck and thread tools.
outer=nose('FullerOuterNose',18.669,43.12)
inner=nose('FullerInnerNose',17.169,41.62)
r10=A.openDocument(str(R10));saved_tool=snapshot('PreservedCapCavityTools',r10.getObject('CapCavityTools').Shape)
saved_outer=snapshot('PreservedCapOuter',r10.getObject('CapOuter').Shape)
saved_tool.addProperty('App::PropertyString','SourceNativeSHA256');saved_tool.SourceNativeSHA256=sha(R10)
A.closeDocument(r10.Name)
rear=op('PreservedCapOuterRear','Common',saved_outer,box('CapRearLimit',[-60,-20,-60,60,54.90,60]))
oldvoid=op('PreservedThreadPilotVoid','Common',saved_tool,box('ThreadPilotVoidLimit',[-60,-20,-60,60,57.05,60]))
newvoid=op('FullerInnerNoseBeyondPilot','Common',inner,box('NewInnerNoseLimit',[-60,57,-60,60,110,60]))
cap_outer=fuse('FullerCapOuter',[rear,outer])
cap=op('FullerClosingCap','Cut',cap_outer,fuse('FullerNoseVoids',[oldvoid,newvoid]));cap.Label='Fuller rounded taper; original rear/thread/pilot tools, nose thermal path needs recheck'

# A PCB cannot slide axially through the fixed motor saddles. Reassign the
# guide lips to the existing keeper so the populated board can drop from +Z.
old_lips=fuse('OriginalGuideLips',[D.getObject('TopRail_1'),D.getObject('TopRail1')])
new_lips=[]
for sign in [-1,1]:
    x0,x1=(8.7,10)if sign>0 else(-10,-8.7)
    new_lips.append(box('KeeperLongRail'+str(sign),[x0,31,.65,x1,54.2,2.15]))
carrier=op('DropInCarrier','Cut',D.getObject('CarrierWithRetainingStem'),fuse('KeeperSeparationTools',[old_lips]+new_lips))
carrier.Label='PCB drops from above; lower/side guides and motor saddles retained'
keeper_blank=fuse('DropInKeeperBlank',[D.getObject('RemovablePCBKeeper')]+new_lips)
clearances=[]
for sign in [-1,1]:
    o=D.addObject('Part::Cylinder','KeeperRailScrewClearance'+str(sign));o.Radius=.9;o.Height=4.6
    o.Placement=A.Placement(A.Vector(sign*10.4,50.3,-.05),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));clearances.append(o)
keeper=op('DropInPCBKeeper','Cut',keeper_blank,fuse('KeeperRailScrewClearances',clearances))
keeper.Label='One U-shaped keeper; same two screw positions; lift off for PCB loading'

superseded=['ClosingNoseCap','CarrierWithRetainingStem','RemovablePCBKeeper','BodyPCBStudy','FrontComponentAllowance','BackComponentAllowance','FlangePCBStudy','FlexibleLinkSpace']
fixed={n:D.getObject(n)for n in report['parts']if n not in superseded}
parts=dict(fixed);parts.update({o.Name:o for o in [cap,carrier,keeper]});pcb_parts={};mates={};input_hashes={}
for domain in ['body','flange']:
    pf=PCB/(domain+'-mechanical-input.json');r=json.loads(pf.read_text());input_hashes[pf.name]=sha(pf)
    assert r['native_board_sha256']==sha(PCB/(domain+'-r12.kicad_pcb'))
    substrate=polygon(domain.title()+'PCB_R12',r['outline_mechanical_xy_mm'],-.5,r['thickness_mm'])
    substrate.addProperty('App::PropertyString','KiCadNativeSHA256');substrate.KiCadNativeSHA256=r['native_board_sha256']
    if domain=='body':pcb_parts[substrate.Name]=substrate
    parts[substrate.Name]=substrate
    for p in r['placements']:
        bb=p['body_xy_mm'];z0,z1=p['z_bounds_mm']
        if not bb or z1-z0<1e-5:continue
        o=box('Placed_'+p['ref'],[bb[0],bb[1],z0,bb[2],bb[3],z1]);o.Label=p['ref']+' Fab / height envelope'
        o.addProperty('App::PropertyString','KiCadNativeSHA256');o.KiCadNativeSHA256=r['native_board_sha256']
        o.addProperty('App::PropertyString','EnvelopeScope');o.EnvelopeScope='Native Fab bounding rectangle and candidate height budget; not a controlled manufacturer maximum/received part.'
        parts[o.Name]=o
        if domain=='body':pcb_parts[o.Name]=o
    for m in r['mates']:
        bb=m['xy_bounds_mm'];z0,z1=m['z_bounds_mm'];o=box('Mate_'+m['ref'],[bb[0],bb[1],z0,bb[2],bb[3],z1])
        mates[o.Name]=o;o.addProperty('App::PropertyString','EnvelopeScope');o.EnvelopeScope=m['scope']
D.recompute()
def inv(s):
    b=s.optimalBoundingBox(False,False);return{'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
for o in list(parts.values())+list(mates.values()):
    want=len(old[o.Name].Solids)if o.Name in fixed else 1
    assert o.Shape.isValid()and len(o.Shape.Solids)==want,(o.Name,inv(o.Shape))
cap_partitions=[]
for z0,z1 in [(-100,0),(0,100)]:
    tool=Part.makeBox(200,250,z1-z0,A.Vector(-100,-100,z0));s=cap.Shape.copy().common(tool)
    assert s.isValid()and len(s.Solids)>0,'Cap Boolean partition must contain material'
    cap_partitions.append({'Z_span_mm':[z0,z1],'volume_mm3':s.Volume,'solids':len(s.Solids)})
assert abs(sum(p['volume_mm3']for p in cap_partitions)-cap.Shape.Volume)<.01,'Cap partition volume must conserve material'
def volume(a,b):
    aa=a.BoundBox;bb=b.BoundBox
    if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))<=max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in 'XYZ'):return 0
    return a.copy().common(b.copy()).Volume
print('R13 valid single solids; checking static pairs',flush=True)
hits=[];named=[];pairs=0
for i,(n,o)in enumerate(parts.items()):
    for m,p in list(parts.items())[i+1:]:
        pairs+=1;v=volume(o.Shape,p.Shape)
        if v<=1e-5:continue
        row={'a':n,'b':m,'intersection_mm3':v}
        if 'DropInCarrier'in[n,m]and any(s.startswith('KeeperScrew')for s in[n,m]):row['scope']='Inherited nominal shaft/pilot interface; formed thread/part/process remains unqualified';named.append(row)
        else:hits.append(row)
mate_hits=[]
for n,o in mates.items():
    for m,p in parts.items():
        if m=='Placed_'+n[5:]:continue
        v=volume(o.Shape,p.Shape)
        if v>1e-5:mate_hits.append({'mate':n,'target':m,'intersection_mm3':v})
print('Static hits',len(hits),'mate hits',len(mate_hits),flush=True)

# Drop board with pack in place, motor and all plugs/keeper waiting.
loading=[]
for offset in [12,8,4,2,1,.5,.25,0]:
    bad=[]
    for n,o in pcb_parts.items():
        s=o.Shape.copy();s.translate(A.Vector(0,0,offset))
        for target in [carrier,D.getObject('NarrowPackAllowance')]:
            v=volume(s,target.Shape)
            if v>1e-5:bad.append({'moving':n,'fixed':target.Name,'intersection_mm3':v})
    loading.append({'Z_offset_mm':offset,'hits':bad})
    print('Drop board',offset,'hits',len(bad),flush=True)
keeper_loading=[]
for offset in [12,8,4,2,1,.5,.25,0]:
    s=keeper.Shape.copy();s.translate(A.Vector(0,0,offset));bad=[]
    for target in [carrier,D.getObject('NarrowPackAllowance')]+list(pcb_parts.values()):
        v=volume(s,target.Shape)
        if v>1e-5:bad.append({'fixed':target.Name,'intersection_mm3':v})
    keeper_loading.append({'Z_offset_mm':offset,'hits':bad})
    print('Lower keeper',offset,'hits',len(bad),flush=True)
# Whole cartridge with the nominal runtime body plugs, then the metal shell.
cartridge_names=[carrier.Name,keeper.Name,'KeeperScrew_1','KeeperScrew1','NarrowPackAllowance','MotorMaxEnvelope']+list(pcb_parts)
cartridge=Part.makeCompound([parts[n].Shape for n in cartridge_names]+[o.Shape for n,o in mates.items()if n in ['Mate_J2','Mate_J3','Mate_J5','Mate_J6']])
cartridge_loading=[]
for offset in range(100,-1,-5):
    s=cartridge.copy();s.translate(A.Vector(0,offset,0));v=volume(s,D.getObject('KeyedOnePieceBody').Shape)
    cartridge_loading.append({'Y_offset_mm':offset,'body_hit_mm3':v});print('Actual-envelope cartridge',offset,v,flush=True)

# Preserve fixed source shapes exactly; new contour is confined to the cap.
unchanged={n:hashlib.sha256(o.Shape.copy().exportBrepToString().encode()).hexdigest()==hashlib.sha256(old[n].copy().exportBrepToString().encode()).hexdigest()for n,o in fixed.items()}
(OUT/'source-role-comparison.json').write_text(json.dumps({'copy_BRep_equal':unchanged,'numeric':{n:{'old':inv(old[n]),'current':inv(o.Shape)}for n,o in fixed.items()}},indent=2)+'\n')
assert all(unchanged.values())
for o in D.Objects:
    if hasattr(o,'ViewObject')and o.ViewObject:o.ViewObject.Visibility=False
for o in list(parts.values())+list(mates.values()):
    if o.ViewObject:o.ViewObject.Visibility=True
for n in ['FlangeCoverUpper','ServiceCoverReference']:
    if D.getObject(n).ViewObject:D.getObject(n).ViewObject.Visibility=False
D.Label='R13 / fuller nose and drop-in two-board placement / NOT BUILD RELEASE'
D.recompute();D.saveAs(str(nf))
native_sha=sha(nf)
mesh_hashes={}
section_tool=Part.makeBox(200,250,100,A.Vector(-100,-100,-100))
for n,o in list(parts.items())+list(mates.items()):
    for suffix,s in [('',o.Shape)]+([('-section',o.Shape.copy().common(section_tool.copy()))]if n in ['KeyedOnePieceBody','FullerClosingCap']else[]):
        if s.Volume<1e-6:continue
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.12,Relative=False)
        f=OUT/(n+suffix+'.stl');mesh.write(str(f));mesh_hashes[f.name]=sha(f)
priorcap=old['ClosingNoseCap'];newcap=cap.Shape;comparison=[]
for y in [54.88,60,70,73.5,80,84.28,88.2,90,92,94,96,97]:
    slab=Part.makeBox(100,.002,100,A.Vector(-50,y-.001,-50))
    bb0=priorcap.common(slab).optimalBoundingBox(False,False);bb1=newcap.common(slab).optimalBoundingBox(False,False)
    comparison.append({'Y_mm':y,'previous_outer_radius_mm':bb0.XLength/2,'fuller_outer_radius_mm':bb1.XLength/2})
out={'date':'2026-11-01','status':'Native development checkpoint; no fabrication or assembly acceptance','builder_sha256':sha(Path(__file__)),
     'native_sha256':native_sha,'source_R11_native_sha256':before,'source_R10_native_sha256':sha(R10),'PCB_directory':str(PCB.relative_to(ROOT)),
     'mechanical_inputs_sha256':input_hashes,'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':{n:inv(o.Shape)for n,o in mates.items()},
     'source_roles_unchanged':unchanged,'superseded_R11_roles':superseded,'static_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_interfaces':named,'nominal_mate_intersections':mate_hits,
     'board_drop_listed_poses':loading,'board_drop_fixed':['DropInCarrier','NarrowPackAllowance'],'board_drop_waiting':['motor','keeper and screws','all plugs/wires','metal body/cap','tip and flange/hub/covers'],
     'keeper_lowering_listed_poses':keeper_loading,'keeper_lowering_fixed':['DropInCarrier','NarrowPackAllowance']+list(pcb_parts),
     'cartridge_listed_poses':cartridge_loading,'cartridge_moving_roles':cartridge_names+['Mate_J2','Mate_J3','Mate_J5','Mate_J6'],
     'cap_boolean_partition_controls':cap_partitions,
     'nose':{'outer_radial_axis_mm':18.669,'outer_axial_axis_mm':43.12,'inner_radial_axis_mm':17.169,'inner_axial_axis_mm':41.62,'maximum_station_Y_mm':54.88,'tip_Y_mm':98,'comparison':comparison,
             'scope':'Same maximum diameter/length/neck. True quarter-ellipse beyond maximum station removes old inflected taper. Internal nose is also fuller; tip thermal shoe/bond must be redesigned. Original R10 thread/pilot void prefix used belowY57; no supplier/finish/wall/fit acceptance.'},
     'review_meshes_sha256':mesh_hashes,'scope':'Actual saved R12 substrates/Fab-height boxes and nominal plugs in R11 source context. New carrier/keeper topology and cap contour native. Finite motion only, no wire routing/flexibility, hands, max tolerances, material/strength, seal/thermal/controls or physical qualification. Boards are UNROUTED. BatteryOPEN; BOM unchanged.'}
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name);assert sha(src)==before and all(sha(PCB/f)==h for f,h in input_hashes.items())
print(json.dumps({'native':str(nf),'parts':len(parts),'static_pairs':pairs,'unexpected':hits,'mate_hits':mate_hits,'board_drop_clear':all(not r['hits']for r in loading),'keeper_lowering_clear':all(not r['hits']for r in keeper_loading),'cartridge_poses_clear':all(r['body_hit_mm3']<1e-5 for r in cartridge_loading)},indent=2),flush=True)
