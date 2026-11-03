"""Fresh saved geometry plus keeper, pad-capture and isolated throat screens."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/interboard-r29/candidate-e';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'geometry-report.json');nf=P/'HarnessSupportR30.FCStd';before=sha(nf);assert before==r['native_sha256']and not r['unexpected_intersections'];D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute()
def bounds(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
roles={};allrows=dict(r['parts'],**r['mates'],**r['allowances'])
for n,q in allrows.items():
 s=D.getObject(n).Shape;dv=s.Volume-q['volume_mm3'];delta=max(abs(a-b)for a,b in zip(bounds(s),q['bounds_xyz_mm']));assert s.isValid()and len(s.Solids)==q['solids']and abs(dv)<1e-4 and delta<1e-5,(n,dv,delta);roles[n]={'valid':True,'solids':len(s.Solids),'volume_delta_mm3':dv,'maximum_bounds_delta_mm':delta}
external=[(o.Name,x.Name)for o in D.Objects for x in o.OutList if x.Document!=D];assert not external
S=A.openDocument(str(SRC/'InterboardR29.FCStd'));conserved={}
for n in r['all_unmodified_source_roles_conserved']:
 a=S.getObject(n).Shape;b=D.getObject(n).Shape;eq=a.exportBrepToString()==b.exportBrepToString();remove,add=(0.,0.)if eq else(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume);assert abs(remove)<1e-4 and abs(add)<1e-4,(n,remove,add);conserved[n]={'exact_BRep_equal':eq,'removed_mm3':remove,'added_mm3':add}
# Removed source material must be contained by the declared pocket/throat/cup
# tools. The body-collar and bolt-bearing regions remain source-identical.
changes={};protected={}
for oldname,newname in r['replaced_roles'].items():
 a=S.getObject(oldname).Shape;b=D.getObject(newname).Shape;removed=a.copy().cut(b.copy());toolnames=['CentralAnchorPocketR30','CentralAnchorWireThroatR30']+(['FlangeCupApproachReliefR30']if oldname=='FlangeSupportHubR27'else[])
 if oldname=='FlangeEndKeeperR27':residual=abs(removed.Volume)
 else:
  tools=Part.makeCompound([D.getObject(n).Shape for n in toolnames]);residual=abs(removed.copy().cut(tools.copy()).Volume)
 assert residual<1e-4,(oldname,residual);changes[oldname]={'replacement':newname,'source_material_removed_mm3':removed.Volume,'outside_declared_cut_tools_removed_mm3':residual}
 if oldname!='FlangeEndKeeperR27':
  regions={'body_collar_Y_minus8_to_minus4_4':Part.makeBox(100,3.6,100,A.Vector(-50,-8,-50)),'upper_hub_bolt_zone':Part.makeBox(100,6,8,A.Vector(-50,-14,5.5)),'lower_hub_bolt_zone':Part.makeBox(100,6,8,A.Vector(-50,-14,-13.5))}
  for label,box in regions.items():
   loss=vol(removed,box);assert loss<1e-5,(oldname,label,loss);protected[oldname+'/'+label]={'source_material_lost_mm3':loss}
A.closeDocument(S.Name)
parts={n:D.getObject(n).Shape for n in r['parts']};mates={n:D.getObject(n).Shape for n in r['mates']};allowances={n:D.getObject(n).Shape for n in r['allowances']};new={n:D.getObject(n).Shape for n in r['new_roles']};named={tuple(sorted([x['a'],x['b']]))for x in r['named_unqualified_screw_pilot_interfaces']};seen=set();hits=[];pilots=[];pairs=0
for n,a in new.items():
 for m,b in dict(parts,**mates,**allowances).items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(a,b)
  if v<=1e-5:continue
  row={'a':n,'b':m,'intersection_mm3':v};(pilots if key in named else hits).append(row)
assert not hits,hits
# Existing one-screw keeper enters from the rear, with covers waiting. All
# wires, both pads and boards are fixed at the stored installed positions.
keeper='HarnessKeeperR30';covers={'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference'};fixed={n:s for n,s in dict(parts,**mates,**allowances).items()if n not in covers|{keeper,'FlangeKeeperScrewEnvelopeR27'}};approach=[]
for y in [-20,-12,-8,-5,-3,-2,-1,-.5,-.25,-.1,0]:
 s=parts[keeper].copy();s.translate(A.Vector(0,y,0));bad=[]
 for n,p in fixed.items():
  v=vol(s,p)
  if v>1e-5:bad.append({'fixed':n,'intersection_mm3':v})
 approach.append({'Y_offset_mm':y,'hits':bad});print('keeper approach',y,bad,flush=True)
# Rigid-pad blocking witnesses; these prove bounded geometric capture, not
# elastomer grip, force ratings or deformation resistance.
captures=[]
for n,keepers in [('CentralAnchorPadR30',['HarnessLeftHubR30','HarnessRightHubR30']),('FlangeAnchorPadR30',['HarnessLeftHubR30',keeper])]:
 for axis in range(3):
  for sign in [-1,1]:
   offset=[0.,0.,0.];offset[axis]=sign*.5;s=parts[n].copy();s.translate(A.Vector(*offset));contact=[{'retainer':m,'intersection_mm3':vol(s,parts[m])}for m in keepers];blocked=any(x['intersection_mm3']>1e-5 for x in contact);captures.append({'pad':n,'offset_xyz_mm':offset,'blocking_witnesses':contact,'blocked_as_rigid':blocked});print('capture',n,offset,blocked,flush=True)
# Finite single-pad transport through metal only. Rotating the flange pad's
# axial Z into body Y keeps its10.8x3.6 section inside the nominal neck.
transport=[];metal=parts['KeyedBodyR25']
for n,rot in [('CentralAnchorPadR30',A.Rotation()),('FlangeAnchorPadR30',A.Rotation(A.Vector(1,0,0),90))]:
 original=parts[n];bb=original.BoundBox;center=A.Vector((bb.XMin+bb.XMax)/2,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2)
 for y in [45,30,20,10,0,-4,-8,-14]:
  s=original.copy();s.Placement=A.Placement(A.Vector(0,y,1.),rot).multiply(A.Placement(-center,A.Rotation())).multiply(s.Placement);v=vol(s,metal);transport.append({'pad':n,'center_Y_mm':y,'metal_intersection_mm3':v})
# Existing screw and generic driver shaft access with the extended keeper.
screw=parts['FlangeKeeperScrewEnvelopeR27'];tool=Part.makeCylinder(1.1,24,A.Vector(-20.5,-45.4,9.1),A.Vector(0,1,0));toolhits=[]
for n,p in dict(parts,**mates).items():
 if n in covers|{'FlangeKeeperScrewEnvelopeR27'}:continue
 v=vol(tool,p)
 if v>1e-5:toolhits.append({'fixed':n,'intersection_mm3':v})
# Export changed parts only; unchanged context meshes remain source-bound.
meshes={}
for n in r['new_roles']:
 f=P/(n+'.stl');MeshPart.meshFromShape(Shape=parts[n],LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'reviewer_sha256':sha(Path(__file__)),'source_R29_native_sha256':r['source_R29_native_sha256'],'saved_roles':roles,'source_roles_conserved':conserved,'external_document_links':external,'changed_material_containment':changes,'protected_interface_witnesses':protected,'forced_new_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':pilots,'keeper_listed_approach_poses':approach,'pads_rigid_translation_blocking_witnesses':captures,'isolated_pad_through_metal_listed_poses':transport,'generic_driver_shaft_hits':toolhits,'changed_role_meshes_sha256':meshes,'all_new_static_keeper_capture_tool_screens_clear':not hits and not any(q['hits']for q in approach)and all(q['blocked_as_rigid']for q in captures)and not toolhits,'scope':'Fresh forced history, source material conservation and declared cut containment. Listed keeper approaches have covers/screw waiting and fixed installed wires/pads. Rigid pad blockers do not prove elastomer/adhesion strength. Isolated centered pads vs metal only, not full connected harness or carrier/plug loading. No actual tool/thread, mold/cure/bond, dynamic movement, load/compliance, RF/seal/physical qualification. Circuit/exterior/motor/tip unchanged; battery OPEN.'};(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('saved review',len(roles),'roles',pairs,'new pairs; stages clear',out['all_new_static_keeper_capture_tool_screens_clear'],'isolated metal hits',[q for q in transport if q['metal_intersection_mm3']>1e-5],flush=True)
