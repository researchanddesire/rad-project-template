"""Fresh forced saved review of the loose-end hub-closure stage."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/harness-support-r30/candidate-b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'parking-review.json');sr=read(SRC/'geometry-report.json');nf=P/'ParkedHarnessR30.FCStd';before=sha(nf);assert before==r['native_sha256']and r['all_listed_geometry_screens_clear']and sha(SRC/'HarnessSupportR30.FCStd')==r['source_R30_native_sha256'];D=A.openDocument(str(nf));old={n:D.getObject(n).Shape.copy()for n in dict(sr['parts'],**sr['mates'],**sr['allowances'])}
for o in D.Objects:o.touch()
D.recompute()
S=A.openDocument(str(SRC/'HarnessSupportR30.FCStd'));conserved={}
for n,a in old.items():
 b=D.getObject(n).Shape;c=S.getObject(n).Shape;assert b.isValid()and len(b.Solids)==len(c.Solids);remove,add=c.copy().cut(b.copy()).Volume,b.copy().cut(c.copy()).Volume;assert abs(remove)<1e-4 and abs(add)<1e-4,(n,remove,add);conserved[n]={'removed_mm3':remove,'added_mm3':add}
A.closeDocument(S.Name);plan=read(ROOT/'hardware/cad/interboard-r29/review-e/wire-plan.json');wires={};rows=[]
for q,w in zip(r['wires'],plan['wires']):
 assert q['pin']==w['pin']and q['net']==w['net'];role=q['role'];s=D.getObject(role).Shape;edges=D.getObject('ParkedPathR30_'+str(q['pin'])).Shape.Edges;expected=edges_from_plan({'curves':w['curves'][:2]});assert len(edges)==3 and abs(sum(e.Length for e in edges)-120)<1e-6 and s.isValid()and len(s.Solids)==1
 errors=[]
 for a,b in zip(edges[:2],expected):
  aa,bb=a.Curve.getPoles(),b.Curve.getPoles();err=max((u-v).Length for u,v in zip(aa,bb));assert len(aa)==len(bb)==6 and err<1e-7;errors.append(err)
 end=edges[-1].Vertexes[-1].Point;assert(end-A.Vector(*q['free_end_xyz_mm'])).Length<1e-7;wires[role]=s;rows.append({'pin':q['pin'],'net':q['net'],'valid':True,'native_external_envelope_length_mm':sum(e.Length for e in edges),'source_prefix_pole_errors_mm':errors,'tail_direction':'Straight -Y; no new bend'})
external=[(o.Name,x.Name)for o in D.Objects for x in o.OutList if x.Document!=D];assert not external
covers=set(r['static_absent_covers']);originalwires={n for n in sr['parts']if n.startswith('InterboardWireR29_')};fixed={n:D.getObject(n).Shape for n in dict(sr['parts'],**sr['mates'],**sr['allowances'])if n not in covers|originalwires|{'FlangeAnchorPadR30'}};fixed.update(wires)
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
seen=set();hits=[];pairs=0
for n,a in wires.items():
 for m,b in fixed.items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(a,b)
  if v>1e-5:hits.append({'a':n,'b':m,'intersection_mm3':v})
 print('fresh parked static',n,flush=True)
assert not hits and pairs==r['new_wire_pairs_tested'],(hits,pairs,r['new_wire_pairs_tested'])
gaps=[{'a':n,'b':m,'native_surface_gap_mm':a.distToShape(b)[0]}for(n,a),(m,b)in itertools.combinations(wires.items(),2)];assert min(q['native_surface_gap_mm']for q in gaps)>0
out={'native_sha256':before,'parking_review_sha256':sha(P/'parking-review.json'),'reviewer_sha256':sha(Path(__file__)),'source_R30_native_sha256':r['source_R30_native_sha256'],'source_current_roles_conserved':conserved,'external_document_links':external,'parked_wires':rows,'new_wire_pairs_tested':pairs,'unexpected_intersections':hits,'wire_surface_gaps':gaps,'all_original_listed_stage_screens_clear':r['all_listed_geometry_screens_clear'],'scope':'Fresh forced saved source material conservation, exact source body-prefix poles and120mm external envelopes, new-wire static/pair checks with declared covers absent. Other waiting objects retained as conservative static obstacles. Stage poses are the source-bound builder checks, not rerun here after geometry conservation. No continuous forming/mating/service, actual endprep/fixtures, cure/bond/load or physical acceptance.'};(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('fresh parked review',len(conserved),'source roles',pairs,'wire comparisons,0hits; min gap',min(q['native_surface_gap_mm']for q in gaps),flush=True)
