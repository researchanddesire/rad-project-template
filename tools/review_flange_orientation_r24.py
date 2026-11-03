"""Read-only review of independently reopened flange pose files."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'orientation-screen.json').read_text())
out={'reviewer_sha256':sha(Path(__file__)),'report_sha256':sha(P/'orientation-screen.json'),'cases':[],
     'scope':'Fresh saved-native validity, local bounds, external-link and fixed-context Boolean review only. No dynamic assembly, flex, RF, control or physical qualification.'}
def bb(shapes):
 b=Part.makeCompound(shapes).BoundBox
 return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0
 return a.copy().common(b.copy()).Volume
for c in r['cases']:
 p=P/c['native_file'];before=sha(p);assert before==c['native_sha256']
 d=A.openDocument(str(p));d.recompute();shapes=[d.getObject(n).Shape for n in r['source_roles']]
 assert all(s.isValid()and len(s.Solids)>0 for s in shapes)
 assert max(abs(a-b)for a,b in zip(bb(shapes),c['populated_bounds_xyz_mm']))<1e-5
 external=[]
 for o in d.Objects:
  for prop in o.PropertiesList:
   if o.getTypeIdOfProperty(prop).startswith('App::PropertyXLink'):external.append(o.Name+'.'+prop)
 assert not external
 hits=[]
 for n in r['source_roles']:
  for m in r['context_roles']:
   v=overlap(d.getObject(n).Shape,d.getObject('Context_'+m).Shape)
   if v>1e-5:hits.append({'moving':n,'fixed':m,'intersection_mm3':v})
 old={(v['moving'],v['fixed']):v['intersection_mm3']for v in c['fixed_context_intersections']}
 new={(v['moving'],v['fixed']):v['intersection_mm3']for v in hits}
 assert old.keys()==new.keys()
 assert all(abs(v-new[k])<1e-5 for k,v in old.items())
 A.closeDocument(d.Name);assert before==sha(p)
 out['cases'].append({'native_file':p.name,'native_sha256':before,'valid_saved_moving_roles':len(shapes),'fixed_pairs_tested':len(shapes)*len(r['context_roles']),'fixed_context_intersections':hits,'external_links':external,'saved_bounds_equal_report':True})
 print(p.name,len(shapes),'saved roles',len(hits),'context hits',flush=True)
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
