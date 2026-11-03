"""Native R20 wider carrier ports and one-piece keeper around actual R17 part poses.

Nominal mates remain allowances, with .3mm cut margins, not accepted installed
connectors. Preserve the R13 fuller cap, 15mm neck and the two-screw keeper.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();PCB=Path(sys.argv[2]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=ROOT/'hardware/cad/simple-assembly-r13/candidate-f/SimpleAssemblyR13.FCStd';before=sha(src);sr=json.loads((src.parent/'geometry-report.json').read_text());assert before==sr['native_sha256'];inp=PCB/'layout-inspection.json';r=json.loads(inp.read_text());D=A.openDocument(str(src));fixed={n:D.getObject(n)for n in sr['parts']if not n.startswith('Placed_')and n not in ['BodyPCB_R12','FlangePCB_R12','DropInCarrier','DropInPCBKeeper']};old={n:o.Shape.copy()for n,o in fixed.items()}
# Widen only the board guides and keeper from 18 to 20 mm. Preserve all
# shell, cap, hub and cover shapes. Source snapshots precede these edits.
modified={}
for o in D.Objects:
 if o.TypeId=='Part::Extrusion' and o.Name.startswith(('BottomRail','SideRail','TopRail')):
  sk=o.Base;assert sk.ConstraintCount==0 and sk.GeometryCount==6
  geometry=[]
  for g in sk.Geometry:
   a,b=g.StartPoint,g.EndPoint
   def widened(v):
    return A.Vector(v.x+(1 if v.x>0 else -1) if v.y>=31-1e-6 else v.x,v.y,v.z)
   geometry.append(Part.LineSegment(widened(a),widened(b)))
  for i in reversed(range(sk.GeometryCount)):sk.delGeometry(i)
  for g in geometry:sk.addGeometry(g,False)
  modified[sk.Name]='wide vertices shifted 1mm outward; rear taper retained'
 if o.TypeId=='Part::Box' and o.Name.startswith(('KeeperLongRail','Riser','RailBridge')):
  v=o.Placement.Base;o.Placement.Base=A.Vector(v.x+(1 if v.x>0 else -1),v.y,v.z);modified[o.Name]='shifted 1mm outward'
 if o.TypeId=='Part::Cylinder' and o.Name.startswith(('KeeperBoss','KeeperPilot','KeeperClearance','KeeperRailScrewClearance','KeeperScrewShaft','KeeperScrewHead')):
  v=o.Placement.Base;assert abs(abs(v.x)-10.4)<1e-6;o.Placement.Base=A.Vector(v.x+(1 if v.x>0 else -1),v.y,v.z);modified[o.Name]='shifted 1mm outward; same two screws with 1mm outward shift'
# The source end plate and screws are explicit R10 snapshots, not the
# original primitives. Rebuild the plate with native primitives, retaining
# the original snapshot in history. Translate the two existing screw budgets.
plate=D.addObject('Part::Box','KeeperEndPlateBlankR20');plate.Length=25.3;plate.Width=.7;plate.Height=2.5;plate.Placement.Base=A.Vector(-12.65,54.1,-1.3)
plateholes=[]
for sign in [-1,1]:
 h=D.addObject('Part::Cylinder','KeeperEndPlateHoleR20'+str(sign));h.Radius=.9;h.Height=1;h.Placement=A.Placement(A.Vector(sign*11.4,54,-.05),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));plateholes.append(h)
holes=D.addObject('Part::MultiFuse','KeeperEndPlateHolesR20');holes.Shapes=plateholes
newplate=D.addObject('Part::Cut','KeeperEndPlateR20');newplate.Base=plate;newplate.Tool=holes
blank=D.getObject('DropInKeeperBlank');blank.Shapes=[newplate if o.Name=='RemovablePCBKeeper'else o for o in blank.Shapes];modified[newplate.Name]='native 25.3mm plate with the two 1.8mm holes at X +/-11.4'
for n in ['KeeperScrew_1','KeeperScrew1']:
 o=D.getObject(n);sign=1 if o.Shape.BoundBox.Center.x>0 else -1;v=o.Placement.Base;o.Placement.Base=A.Vector(v.x+sign,v.y,v.z);modified[n]='source screw budget shifted 1mm outward'

widths=D.addObject('Spreadsheet::Sheet','WidthInputsR20');widths.set('A1','PCB maximum width');widths.set('B1','=20 mm');widths.setAlias('B1','BoardWidth');D.recompute()

def box(n,bb):
 x,y,z,a,b,c=bb;o=D.addObject('Part::Box',n);o.Length=a-x;o.Width=b-y;o.Height=c-z;o.Placement.Base=A.Vector(x,y,z);return o
def fuse(n,parts):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=parts;o.Refine=True;return o
def cut(n,a,b):
 o=D.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
tools=[];port_bounds={}
for m in r['boards']['body']['mates']:
 if m['ref']not in ['J2','J3','J5']:continue
 a,b,c,e=m['xy_bounds_mm'];z0,z1=m['z_bounds_mm'];bb=[a-.3,b-.3,z0-.3,c+.3,e+.3,z1+.3];port_bounds[m['ref']]=bb;tools.append(box('PortR20_'+m['ref'],bb))
tool=fuse('ConnectorPortToolsR20',tools)
carrier=cut('PortedCarrierR20',D.getObject('DropInCarrier'),tool)
# Windowing the left keeper rail alone would leave its forward section loose.
# A continuous outside bridge and two ties retain one keeper and two screws.
bridge_bounds={'OutsideBridge':[-11.25,34.5,.65,-10.45,46.5,2.15],'ForeTie':[-11.25,34.5,.65,-8.7,35.2,2.15],'AftTie':[-11.25,45.8,.65,-8.7,46.5,2.15]}
bridges=[box('KeeperR20_'+n,bb)for n,bb in bridge_bounds.items()]
keeper=cut('PortedKeeperR20',fuse('BridgedKeeperR20',[D.getObject('DropInPCBKeeper')]+bridges),tool)
carrier.Label='Drop-in carrier / three nominal connector ports'
keeper.Label='One keeper / outside battery-plug bridge / same two screws with 1mm outward shift'
parts=dict(fixed);parts.update({carrier.Name:carrier,keeper.Name:keeper});body_parts={};mates={};boards={}
for domain,board in r['boards'].items():
 bp=next((PCB/domain).glob(domain+'-r*.kicad_pcb'));assert sha(bp)==board['native_board_sha256'];boards[domain]=sha(bp)
 sk=D.addObject('Sketcher::SketchObject',domain.title()+'R17Outline');sk.Placement.Base.z=-.5;pts=board['outline_xy_mm']
 for a,b in zip(pts,pts[1:]+pts[:1]):sk.addGeometry(Part.LineSegment(A.Vector(*a,0),A.Vector(*b,0)),False)
 o=D.addObject('Part::Extrusion',domain.title()+'PCB_R17');o.Base=sk;o.Dir=A.Vector(0,0,1);o.LengthFwd=board['thickness_mm'];o.Solid=True;parts[o.Name]=o
 if domain=='body':body_parts[o.Name]=o
 for q in board['placements']:
  if not q['body_xy_mm']:continue
  a,b,c,e=q['body_xy_mm'];z0,z1=q['z_bounds_mm'];o=box('R17_'+q['ref'],[a,b,z0,c,e,z1]);o.Label=q['ref']+' actual Fab / candidate height budget';parts[o.Name]=o
  if domain=='body':body_parts[o.Name]=o
 for m in board['mates']:
  a,b,c,e=m['xy_bounds_mm'];z0,z1=m['z_bounds_mm'];o=box('R17Mate_'+m['ref'],[a,b,z0,c,e,z1]);mates[o.Name]=o
 for o in [parts[n]for n in parts if n.endswith('_R17')or n.startswith('R17_')]+list(mates.values()):
  if not hasattr(o,'EnvelopeScope'):o.addProperty('App::PropertyString','EnvelopeScope');o.EnvelopeScope='Native PCB Fab/height envelope or nominal mating allowance; no controlled part maximum, wire or physical fit acceptance.'
D.recompute()
def inv(s):
 b=s.optimalBoundingBox(False,False);return{'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,n)for n in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
for n,o in list(parts.items())+list(mates.items()):assert o.Shape.isValid()and len(o.Shape.Solids)==(len(old[n].Solids)if n in fixed else 1),(n,inv(o.Shape))
def volume(a,b):
 aa=a.BoundBox;bb=b.BoundBox
 if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))<=max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in 'XYZ'):return 0
 return a.copy().common(b.copy()).Volume
hits=[];named=[];pairs=0
for (n,o),(m,p)in itertools.combinations(parts.items(),2):
 pairs+=1;v=volume(o.Shape,p.Shape)
 if v<1e-5:continue
 row={'a':n,'b':m,'intersection_mm3':v}
 if 'PortedCarrierR20'in [n,m]and any(k.startswith('KeeperScrew')for k in [n,m]):named.append(row)
 else:hits.append(row)
matehits=[]
for n,o in mates.items():
 for m,p in parts.items():
  if m=='R17_'+n.removeprefix('R17Mate_'):continue
  v=volume(o.Shape,p.Shape)
  if v>1e-5:matehits.append({'mate':n,'target':m,'intersection_mm3':v})
print('R20 static',pairs,'unexpected',hits,'mates',matehits,flush=True)
loading=[];keeper_loading=[];cartridge=[]
for z in [12,8,4,2,1,.5,.25,0]:
 bad=[]
 for n,o in body_parts.items():
  s=o.Shape.copy();s.translate(A.Vector(0,0,z))
  for target in [carrier,D.getObject('NarrowPackAllowance')]:
   v=volume(s,target.Shape)
   if v>1e-5:bad.append([n,target.Name,v])
 loading.append({'Z_offset_mm':z,'hits':bad})
 s=keeper.Shape.copy();s.translate(A.Vector(0,0,z));bad=[]
 for target in [carrier,D.getObject('NarrowPackAllowance')]+list(body_parts.values()):
  v=volume(s,target.Shape)
  if v>1e-5:bad.append([target.Name,v])
 keeper_loading.append({'Z_offset_mm':z,'hits':bad})
moving=[carrier,keeper,D.getObject('KeeperScrew_1'),D.getObject('KeeperScrew1'),D.getObject('NarrowPackAllowance'),D.getObject('MotorMaxEnvelope')]+list(body_parts.values())+[mates['R17Mate_'+n]for n in ['J2','J3','J5','J6']]
for y in range(100,-1,-5):
 bad=[]
 for o in moving:
  s=o.Shape.copy();s.translate(A.Vector(0,y,0));v=volume(s,D.getObject('KeyedOnePieceBody').Shape)
  if v>1e-5:bad.append({'role':o.Name,'body_hit_mm3':v})
 cartridge.append({'Y_offset_mm':y,'body_hit_mm3':sum(q['body_hit_mm3']for q in bad),'hits':bad})
 print('cartridge Y',y,'hits',bad,flush=True)

unchanged={n:{'before':inv(old[n]),'after':inv(o.Shape),'symmetric_material_difference_mm3':old[n].cut(o.Shape).Volume+o.Shape.cut(old[n]).Volume}for n,o in fixed.items()}
assert all(v['symmetric_material_difference_mm3']<.01 for n,v in unchanged.items()if not n.startswith('KeeperScrew'))
for o in D.Objects:
 if hasattr(o,'ViewObject')and o.ViewObject:o.ViewObject.Visibility=False
for o in list(parts.values())+list(mates.values()):
 if o.ViewObject:o.ViewObject.Visibility=True
for n in ['FlangeCoverUpper','ServiceCoverReference']:
 if D.getObject(n).ViewObject:D.getObject(n).ViewObject.Visibility=False
D.Label='R20 / native PCB integration and ported one-piece keeper / DEVELOPMENT'
nf=P/'PCBIntegrationR20.FCStd';D.recompute();D.saveAs(str(nf));meshhash={};section=Part.makeBox(200,250,100,A.Vector(-100,-100,-100))
for n,o in list(parts.items())+list(mates.items()):
 for suffix,s in [('',o.Shape)]+([('-section',o.Shape.copy().common(section.copy()))]if n in ['KeyedOnePieceBody','FullerClosingCap']else[]):
  if s.Volume<1e-6:continue
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.12,Relative=False);f=P/(n+suffix+'.stl');mesh.write(str(f));meshhash[f.name]=sha(f)
out={'date':'2026-11-01','builder_sha256':sha(Path(__file__)),'source_R13_native_sha256':before,'PCB_directory':str(PCB.relative_to(ROOT)),'PCB_inspection_sha256':sha(inp),'PCB_native_sha256':boards,'native_sha256':sha(nf),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':{n:inv(o.Shape)for n,o in mates.items()},'port_cut_bounds_xyz_mm':port_bounds,'keeper_bridge_bounds_xyz_mm':bridge_bounds,'widened_native_features':modified,'declared_source_geometry_changes':['KeeperScrew_1','KeeperScrew1'],'retained_source_material_comparison':unchanged,'static_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':named,'nominal_mate_intersections':matehits,'board_drop_listed_poses':loading,'keeper_lowering_listed_poses':keeper_loading,'cartridge_listed_poses':cartridge,'cartridge_roles':[o.Name for o in moving],'review_meshes_sha256':meshhash,'scope':'Actual saved native PCB part/substrate poses; nominal connector allowance ports with .3mm margin. Outside bridge keeps one keeper and same two screws with 1mm outward shift. Source exterior/full nose/15mm neck preserved. Finite rigid poses only; no real wires, flex, contact maxima, retention loads/material/print/process/seal/control/tip acceptance. Battery OPEN. No build release.'}
(P/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(src)==before
print(json.dumps({'native':str(nf),'unexpected':hits,'mates':matehits,'board_drop_clear':all(not q['hits']for q in loading),'keeper_clear':all(not q['hits']for q in keeper_loading),'cartridge_clear':all(q['body_hit_mm3']<1e-5 for q in cartridge)},indent=2),flush=True)
