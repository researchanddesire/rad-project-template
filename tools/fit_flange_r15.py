"""Source-bound exact static R15 flange envelopes in retained R13F context."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();P=a.directory.resolve();rf=P/'flange-native-inspection.json';r=json.loads(rf.read_text());assert r['native_board_sha256']==sha(P/'flange/flange-r15.kicad_pcb')
CAD=ROOT/'hardware/cad/simple-assembly-r13/candidate-f';nf=CAD/'SimpleAssemblyR13.FCStd';cr=json.loads((CAD/'geometry-report.json').read_text());before=sha(nf);assert before==cr['native_sha256'];d=A.openDocument(str(nf));refs={p['ref']for p in r['placements']}
excluded=['FlangePCB_R12']+['Placed_'+ref for ref in refs];fixed={n:d.getObject(n).Shape.copy()for n in cr['parts']if n not in excluded};fixed.update({n:d.getObject(n).Shape.copy()for n in cr['mates']if n[5:]not in refs})
pts=[A.Vector(x,y,-.5)for x,y in r['outline_mechanical_xy_mm']];new={'NewFlangeSubstrate':Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,1))}
def shape(bb,zz):return Part.makeBox(bb[2]-bb[0],bb[3]-bb[1],zz[1]-zz[0],A.Vector(bb[0],bb[1],zz[0]))
for p in r['placements']:new[p['ref']]=shape(p['body_xy_mm'],p['z_bounds_mm'])
def volume(a,b):
 aa=a.BoundBox;bb=b.BoundBox
 if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))<=max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in'XYZ'):return 0
 return a.copy().common(b.copy()).Volume
hits=[];mate_hits=[]
for n,s in new.items():
 for name,t in fixed.items():
  v=volume(s,t)
  if v>1e-5:hits.append({'new':n,'fixed':name,'intersection_mm3':v})
for m in r['mates']:
 s=shape(m['xy_bounds_mm'],m['z_bounds_mm'])
 for name,t in dict(fixed,**new).items():
  if name==m['ref']:continue
  v=volume(s,t)
  if v>1e-5:mate_hits.append({'mate':m['ref'],'target':name,'intersection_mm3':v,'service_only':m['service_only']})
out={'source_R13_native_sha256':before,'new_board_sha256':r['native_board_sha256'],'inspection_sha256':sha(rf),'reviewer_sha256':sha(Path(__file__)),'excluded_superseded_roles':excluded,'fixed_roles':list(fixed),'new_primary_roles':list(new),'primary_fixed_pairs_tested':len(new)*len(fixed),'component_intersections':hits,'nominal_mate_intersections':mate_hits,'scope':'Read-only static Fab/height and nominal SH mates against retained87R13primary+4bodymate roles. No native CAD integration, working wing support/controls, wires, loads, tolerances or physical fit acceptance.'}
A.closeDocument(d.Name);assert sha(nf)==before;(P/'flange-mechanical-fit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pairs':out['primary_fixed_pairs_tested'],'body_hits':hits,'mate_hits':mate_hits},indent=2),flush=True)
