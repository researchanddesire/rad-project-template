"""Add actual native swept individual wire allowances to a saved tip study."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher,MeshPart
from tip_wire_native_r26 import edges_from_plan
SOURCE=Path(sys.argv[1]).resolve();PLAN=Path(sys.argv[2]).resolve();OUT=Path(sys.argv[3]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((SOURCE/'geometry-report.json').read_text());plan=json.loads(PLAN.read_text());nf=SOURCE/'StationaryTipR26.FCStd';assert sha(nf)==r['native_sha256']
D=A.openDocument(str(nf));old={n:D.getObject(n).Shape.copy()for n in r['parts']};parts={n:D.getObject(n)for n in r['parts']};mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']}
new={};rows=[]
for q in plan['wires']:
 assert q['minimum_sampled_polynomial_centerline_radius_mm']>=2.5
 edges=edges_from_plan(q)
 spine=D.addObject('Part::Feature','TipWirePathR26_'+str(q['pin']));spine.Shape=Part.Wire(edges)
 start=q['J5_wire_exit_nominal_xyz_mm'];profile=D.addObject('Sketcher::SketchObject','TipWireProfileR26_'+str(q['pin']));profile.Placement=A.Placement(A.Vector(*start),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),q['insulation_OD_allowance_mm']/2),False)
 wire=D.addObject('Part::Sweep','TipWireR26_'+str(q['pin']));wire.Sections=[profile];wire.Spine=spine;wire.Solid=True;wire.Frenet=True;wire.Label=q['net']+' individual insulation allowance / OD0.60mm / polynomial and circular path'
 a,b=[A.Vector(*p)for p in q['bare_segment_xyz_mm']];delta=b-a
 bare=D.addObject('Part::Cylinder','TipBareWireR26_'+str(q['pin']));bare.Radius=q['bare_OD_allowance_mm']/2;bare.Height=delta.Length;bare.Placement=A.Placement(a,A.Rotation(A.Vector(0,0,1),delta))
 bare.Label=q['net']+' bare tail allowance / OD0.26mm /1.1mm strip study'
 x,y,z=q['J101_pad_center_xyz_mm'];solder=D.addObject('Part::Box','TipSolderAllowanceR26_'+str(q['pin']));solder.Length=.8;solder.Width=.35;solder.Height=1.025;solder.Placement.Base=A.Vector(x-.4,y-.35,z-.6)
 solder.Label=q['net']+' solder-fillet allowance / wetting/process unqualified'
 for o in [wire,bare,solder]:parts[o.Name]=o;new[o.Name]=o
 D.recompute();assert wire.Shape.isValid()and len(wire.Shape.Solids)==1
 length=spine.Shape.Length;assert abs(length-q['sampled_insulated_centerline_length_mm'])<.001,(q['pin'],length,q['sampled_insulated_centerline_length_mm'])
 rows.append({'pin':q['pin'],'net':q['net'],'native_insulated_centerline_length_mm':length,'planned_insulated_length_mm':q['sampled_insulated_centerline_length_mm'],'native_path_edges':len(edges),'wire_role':wire.Name,'bare_role':bare.Name,'solder_role':solder.Name})
 print('native wire',q['pin'],length,flush=True)
def inv(s):
 b=s.optimalBoundingBox(False,False)
 return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0
 return a.copy().common(b.copy()).Volume
conserved={}
for n,s in old.items():
 now=parts[n].Shape;equal=s.exportBrepToString()==now.exportBrepToString();a,b=(0,0)if equal else(s.copy().cut(now.copy()).Volume,now.copy().cut(s.copy()).Volume)
 assert a<1e-4 and b<1e-4,(n,a,b);conserved[n]={'removed_mm3':a,'added_mm3':b,'exact_BRep_equal':equal}
hits=[];intentional=[];seen=set();pairs=0
for n,o in new.items():
 for m,p in parts.items():
  if n==m:continue
  key=tuple(sorted([n,m]))
  if key in seen:continue
  seen.add(key);pairs+=1;v=vol(o.Shape,p.Shape)
  if v<=1e-5:continue
  row={'a':n,'b':m,'intersection_mm3':v}
  samepin=n.rsplit('_',1)[-1]==m.rsplit('_',1)[-1]
  if samepin and all(x in new for x in [n,m]):intentional.append(row)
  else:hits.append(row)
matehits=[];flarehits=[]
for n,o in new.items():
 for m,p in mates.items():
  v=vol(o.Shape,p.Shape)
  if v>1e-5:matehits.append({'wire':n,'mate':m,'intersection_mm3':v})
 for m,p in allowances.items():
  if m=='TipStrainReliefProcessAllowanceR26':continue
  v=vol(o.Shape,p.Shape)
  if v>1e-5:flarehits.append({'wire':n,'allowance':m,'intersection_mm3':v})
gaps=[]
for a,b in itertools.combinations(rows,2):
 o,p=D.getObject(a['wire_role']),D.getObject(b['wire_role']);gaps.append({'pins':[a['pin'],b['pin']],'native_insulation_surface_distance_mm':o.Shape.distToShape(p.Shape)[0]})
pot=allowances['TipStrainReliefProcessAllowanceR26'];embedded={q['pin']:vol(D.getObject(q['wire_role']).Shape,pot.Shape)for q in rows}
out=dict(r);out['builder_sha256']=sha(Path(__file__));out['native_wire_library_sha256']=sha(Path(__file__).with_name('tip_wire_native_r26.py'));out['source_R26_native_sha256']=r['native_sha256'];out['source_R26_report_sha256']=sha(SOURCE/'geometry-report.json');out['wire_plan_sha256']=sha(PLAN);out['wire_plan_path']=str(PLAN);out['parts']={n:inv(o.Shape)for n,o in parts.items()};out['preserved_source_R26_roles']=conserved;out['new_wire_pairs_tested']=pairs;out['new_wire_unexpected_intersections']=hits;out['same_net_solder_tail_interfaces']=intentional;out['new_wire_nominal_mate_intersections']=matehits;out['new_wire_conditional_flare_intersections']=flarehits;out['individual_wire_native_geometry']=rows;out['wire_pair_surface_gaps']=gaps;out['strain_relief_wire_overlap_mm3']=embedded
print('wire hits',hits,'mates',matehits,'flare',flarehits,'gaps',gaps,flush=True)
out['scope']='Current native stationary tip support plus four swept insulated wires with C2 polynomial transitions and tangent-continuous circular bends, bare-tail and solder allowances. Source roles unchanged. Assumed J5 egress datum, OD/bend/termination allowances and candidate process only; no actual crimp, strip/solder, service motion, cure/strength, thermal/electrical or physical qualification. BatteryOPEN.'
D.Label='R26 / stationary tip and four individual routed wires / DEVELOPMENT';output=OUT/'StationaryTipR26.FCStd';D.recompute();D.saveAs(str(output));out['native_sha256']=sha(output)
meshes={};side=Part.makeBox(100,250,100,A.Vector(-100,-100,-50))
for n,o in dict(parts,**mates,**allowances).items():
 for suffix,s in [('',o.Shape)]+([('-side-section',o.Shape.copy().common(side.copy()))]if n in ['KeyedBodyR25','MotorSeatCapR25','ShellMotorMountR25','StationaryTipCarrierR26']else[]):
  if s.Volume<1e-6:continue
  f=OUT/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
out['review_meshes_sha256']=meshes;(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==r['native_sha256'];print('saved',output,flush=True)
