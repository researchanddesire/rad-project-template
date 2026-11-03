"""Fresh forced saved-history review of R29 wires and unchanged R27 roles."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();PLAN=Path(sys.argv[2]).resolve();SRC=ROOT/'hardware/cad/flange-controls-r27/candidate-d';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'geometry-report.json');plan=read(PLAN);nf=P/'InterboardR29.FCStd';before=sha(nf);assert before==r['native_sha256']and sha(PLAN)==r['plan_sha256']and not r['new_wire_intersections']
D=A.openDocument(str(nf))
for o in D.Objects:o.touch()
D.recompute()
def bb(s):
 b=s.optimalBoundingBox(False,False);return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
roles={}
for n,q in dict(r['parts'],**r['mates'],**r['allowances']).items():
 s=D.getObject(n).Shape;delta=max(abs(a-b)for a,b in zip(bb(s),q['bounds_xyz_mm']));dv=s.Volume-q['volume_mm3'];assert s.isValid()and len(s.Solids)==q['solids']and delta<1e-5 and abs(dv)<1e-4,(n,delta,dv)
 roles[n]={'valid':True,'solids':len(s.Solids),'maximum_bounds_delta_mm':delta,'volume_delta_mm3':dv}
external=[(o.Name,x.Name)for o in D.Objects for x in o.OutList if x.Document!=D];assert not external
S=A.openDocument(str(SRC/'FlangeCradleR27.FCStd'));source=read(SRC/'geometry-report.json');conserved={}
for n in dict(source['parts'],**source['mates'],**source['allowances']):
 a=S.getObject(n).Shape;b=D.getObject(n).Shape;exact=a.exportBrepToString()==b.exportBrepToString();remove,add=(0.,0.)if exact else(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume);assert abs(remove)<1e-4 and abs(add)<1e-4,(n,remove,add);conserved[n]={'exact_BRep_equal':exact,'removed_mm3':remove,'added_mm3':add}
A.closeDocument(S.Name)
paths=[];meshes={}
for q in plan['wires']:
 edges=D.getObject('InterboardPathR29_'+str(q['pin'])).Shape.Edges;wanted=edges_from_plan(q);assert len(edges)==len(wanted)
 errors=[]
 for a,b in zip(edges,wanted):
  assert abs(a.Length-b.Length)<1e-6
  if q['curves'][len(errors)]['kind']=='bezier5':
   aa,bbp=a.Curve.getPoles(),b.Curve.getPoles();assert len(aa)==len(bbp)==6;err=max((x-y).Length for x,y in zip(aa,bbp));assert err<1e-7
  else:
   err=max(abs(a.Curve.Radius-b.Curve.Radius),(a.Curve.Center-b.Curve.Center).Length);assert err<1e-7
  errors.append(err)
 role='InterboardWireR29_'+str(q['pin']);s=D.getObject(role).Shape;file=P/(role+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.12,Relative=False).write(str(file));meshes[file.name]=sha(file);paths.append({'pin':q['pin'],'exact_stored_curve_errors_mm':errors,'native_centerline_length_mm':sum(e.Length for e in edges)})
# Recheck every new-wire pair against all final source roles after forcing history.
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
wires={q['role']:D.getObject(q['role']).Shape for q in r['individual_wires']};allroles={n:D.getObject(n).Shape for n in roles};seen=set();hits=[];pairs=0
for n,a in wires.items():
 for m,b in allroles.items():
  if n==m:continue
  key=tuple(sorted([n,m]))
  if key in seen:continue
  seen.add(key);pairs+=1;v=vol(a,b)
  if v>1e-5:hits.append({'a':n,'b':m,'intersection_mm3':v})
 print('forced wire static',n,flush=True)
gaps=[{'a':n,'b':m,'native_surface_distance_mm':a.distToShape(b)[0]}for(n,a),(m,b)in itertools.combinations(wires.items(),2)];assert not hits and all(q['native_surface_distance_mm']>0 for q in gaps),(hits,gaps)
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'plan_sha256':sha(PLAN),'plan_review_sha256':sha(PLAN.with_name('plan-review.json')),'reviewer_sha256':sha(Path(__file__)),'path_library_sha256':sha(Path(__file__).with_name('tip_wire_native_r26.py')),'saved_roles':roles,'source_R27_roles_conserved':conserved,'external_document_links':external,'stored_exact_curve_comparison':paths,'forced_new_pairs_tested':pairs,'unexpected_intersections':hits,'native_wire_surface_gaps':gaps,'wire_review_meshes_sha256':meshes,'scope':'Fresh forced saved-history/role validity and source material conservation; exact stored Bezier poles/circle centre/radius; every new wire vs all final source roles and other wires. Inherited source static pairs are unchanged and not rerun here. Geometry uses assumed mated wire exits and OD allowance, not actual part tolerances, supports/strain relief, assembly/service motion or dynamic flex/electrical/physical acceptance. Source circuit, exterior and human BOM unchanged; battery OPEN.'};(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('saved roles',len(roles),'source conserved',len(conserved),'pairs',pairs,'hits',len(hits),'minimum wire gap',min(q['native_surface_distance_mm']for q in gaps),flush=True)
