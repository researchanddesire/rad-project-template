"""Read-only R16 two-board replacement screen in exact R13F native context."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inp=P/'layout-inspection.json';r=json.loads(inp.read_text());cad=ROOT/'hardware/cad/simple-assembly-r13/candidate-f/SimpleAssemblyR13.FCStd';before=sha(cad);cr=json.loads((cad.parent/'geometry-report.json').read_text());assert before==cr['native_sha256'];d=A.openDocument(str(cad));fixed={n:d.getObject(n).Shape.copy()for n in cr['parts']if not n.startswith('Placed_')and n not in ['BodyPCB_R12','FlangePCB_R12']};new={};mates={};pad_only=[]
def box(bb,zz):return Part.makeBox(bb[2]-bb[0],bb[3]-bb[1],zz[1]-zz[0],A.Vector(bb[0],bb[1],zz[0]))
for domain,b in r['boards'].items():
 assert sha(P/domain/(domain+'-r16.kicad_pcb'))==b['native_board_sha256']
 pts=[A.Vector(x,y,-.5)for x,y in b['outline_xy_mm']];new[domain+'_substrate']=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,1))
 for p in b['placements']:
  if p['height_budget_mm']==0 and p['body_xy_mm']is None:pad_only.append(p['ref']);continue
  new[p['ref']]=box(p['body_xy_mm'],p['z_bounds_mm'])
 for m in b['mates']:mates[m['ref']]=box(m['xy_bounds_mm'],m['z_bounds_mm'])
def volume(a,b):
 aa=a.BoundBox;bb=b.BoundBox
 if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))<=max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in 'XYZ'):return 0
 return a.copy().common(b.copy()).Volume
hits=[];mhits=[];pairs=0
for n,s in new.items():
 for name,t in fixed.items():
  pairs+=1;v=volume(s,t)
  if v>1e-5:hits.append({'new':n,'fixed':name,'mm3':v})
for (n,s),(name,t)in itertools.combinations(new.items(),2):
 pairs+=1;v=volume(s,t)
 if v>1e-5:hits.append({'new':n,'new_other':name,'mm3':v})
for n,s in mates.items():
 for name,t in dict(fixed,**new).items():
  if name==n:continue
  v=volume(s,t)
  if v>1e-5:mhits.append({'mate':n,'target':name,'mm3':v})
out={'date':'2026-11-01','reviewer_sha256':sha(Path(__file__)),'R13_native_sha256':before,'inspection_sha256':sha(inp),'retained_fixed_roles':list(fixed),'new_primary_roles':list(new),'pad_only_parts_without_3D_body':pad_only,'new_primary_pairs':pairs,'primary_intersections':hits,'nominal_mate_intersections':mhits,'scope':'Exact R13F retained native roles plus actual part/substrate envelopes and nominal connector mates; pad-onlyJP1 has no3Dbody. Only new-vs-fixed/new pairs screened. Preserved fixed pairs retain their R13 source record. No savedCAD integration, real terminals/wires/loads/paths/tolerances/physical fit acceptance.'};A.closeDocument(d.Name);assert sha(cad)==before;(P/'mechanical-fit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pairs':pairs,'primary_hits':hits,'mate_hits':mhits},indent=2),flush=True)
