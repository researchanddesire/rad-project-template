"""Source-bound free-end wire parking for hub closure before flange forming.

The120mm external straight-tail envelope overbounds starting stock after body
end prep; shorter loose ends are contained in the same clear tail corridor.
No preformed flange loop, flange pad or J7 housing is present at this stage.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher,MeshPart
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());nf=P/'HarnessSupportR30.FCStd';r=read(P/'geometry-report.json');planpath=ROOT/'hardware/cad/interboard-r29/review-e/wire-plan.json';plan=read(planpath);assert sha(nf)==r['native_sha256'];D=A.openDocument(str(nf));new={};wireinfo=[]
for w in plan['wires']:
 edges=edges_from_plan({'curves':w['curves'][:2]});start=edges[-1].Vertexes[-1].Point;prefix=sum(e.Length for e in edges);length=120-prefix;assert length>60;end=start+A.Vector(0,-length,0);edges.append(Part.makeLine(start,end));spine=D.addObject('Part::Feature','ParkedPathR30_'+str(w['pin']));spine.Shape=Part.Wire(edges)
 prof=D.addObject('Sketcher::SketchObject','ParkedProfileR30_'+str(w['pin']));prof.Placement=A.Placement(A.Vector(*w['start_xyz_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(0,-1,0)));prof.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),.3),False);wire=D.addObject('Part::Sweep','ParkedWireR30_'+str(w['pin']));wire.Sections=[prof];wire.Spine=spine;wire.Solid=True;wire.Frenet=True;wire.Label=str(w['pin'])+' / '+w['net']+' / free flange end120mm external stock envelope';D.recompute();assert wire.Shape.isValid()and len(wire.Shape.Solids)==1;new[wire.Name]=wire.Shape;wireinfo.append({'pin':w['pin'],'net':w['net'],'role':wire.Name,'prefix_native_length_mm':prefix,'external_envelope_length_mm':spine.Shape.Length,'free_end_xyz_mm':list(end)})
r27=read(ROOT/'hardware/cad/flange-controls-r27/candidate-d/geometry-report.json');island=set(r27['inverse_transformed_flange_roles']);covers={'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference'};hardware={'HubBolt_1','HubBolt1','HubNut_1','HubNut1','FlangeKeeperScrewEnvelopeR27'};keeper={'HarnessKeeperR30'}
oldwires={n for n in r['parts']if n.startswith('InterboardWireR29_')};notformed={'FlangeAnchorPadR30'}
allparts={n:D.getObject(n).Shape for n in dict(r['parts'],**r['mates'],**r['allowances'])if n not in oldwires|notformed};allparts.update(new)
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
seen=set();hits=[];pairs=0
for n,a in new.items():
 for m,b in allparts.items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen or m in covers:continue
  seen.add(key);pairs+=1;v=vol(a,b)
  if v>1e-5:hits.append({'a':n,'b':m,'intersection_mm3':v})
print('parked static',pairs,hits,flush=True)
def poses(names,fixed,offsets):
 result=[]
 for x in offsets:
  bad=[]
  for n in names:
   s=allparts[n].copy();s.translate(A.Vector(x,0,0))
   for m,p in fixed.items():
    v=vol(s,p)
    if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
  result.append({'X_offset_mm':x,'hits':bad});print(names[0],x,bad,flush=True)
 return result
waiting=island|covers|hardware|keeper
left=poses(['HarnessLeftHubR30'],{n:s for n,s in allparts.items()if n not in waiting|{'HarnessLeftHubR30'}},[-30,-20,-10,-5,-2,-1,-.5,-.25,0]);right=poses(['HarnessRightHubR30'],{n:s for n,s in allparts.items()if n not in waiting|{'HarnessRightHubR30'}},[30,20,10,5,2,1,.5,.25,0]);board=sorted(n for n in island if n in r['parts']);bf={n:s for n,s in allparts.items()if n not in set(board)|covers|keeper|{n for n in r['mates']if n in island}|{'FlangeKeeperScrewEnvelopeR27'}};flange=poses(board,bf,[-50,-40,-30,-20,-10,-5,-2,-1,-.5,-.25,0])
gaps=[{'a':n,'b':m,'native_surface_distance_mm':a.distToShape(b)[0]}for(n,a),(m,b)in itertools.combinations(new.items(),2)];assert all(q['native_surface_distance_mm']>0 for q in gaps)
meshes={}
for n,s in new.items():
 f=OUT/(n+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
output=OUT/'ParkedHarnessR30.FCStd';D.Label='R30 / free flange ends parked for hub closure / assembly stage';D.saveAs(str(output));report={'source_R30_native_sha256':sha(nf),'source_R30_report_sha256':sha(P/'geometry-report.json'),'source_R29_complete_plan_sha256':sha(planpath),'builder_screener_sha256':sha(Path(__file__)),'native_sha256':sha(output),'wires':wireinfo,'static_absent_covers':sorted(covers),'new_wire_pairs_tested':pairs,'unexpected_static_intersections':hits,'native_wire_surface_gaps':gaps,'left_hub_listed_poses':left,'right_hub_listed_poses':right,'populated_flange_listed_poses':flange,'all_listed_geometry_screens_clear':not hits and not any(q['hits']for q in left+right+flange),'review_meshes_sha256':meshes,'stage':'Body/carrier/J6 and central pad seated; all ten flange ends loose, unstripped/unhoused, with straight free tails. Flange pad not cast yet. Hub and flange movements have covers/fasteners/keeper and nominal mates waiting as recorded.','scope':'Complete individual parked wire geometry and finite hub/flange poses, not continuous travel or modeled hands/fixture.120mm external envelope overbounds starting stock after body end prep, not finished cut length/material conservation. Curved body prefix unchanged; straight tails add no bends. Form/trim/terminate loose flange ends after hub closure, then cast/cure flange pad externally before keeper fit. Does not prove the wire-forming transition, actual contacts/mating, overmold adhesion/cure/loads, service movement, current/RF/physical assembly.'};(OUT/'parking-review.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==r['native_sha256'];print('parked assembly clear',report['all_listed_geometry_screens_clear'],flush=True)
