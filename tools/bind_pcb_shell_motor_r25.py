"""Read-only native PCB substrate/Fab envelope binding to the current circuit."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();PCB=Path(sys.argv[2]).resolve();OUT=Path(sys.argv[3]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
nf=P/'ShellMotorMountR25.FCStd';r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text())
assert sha(nf)==r['native_sha256']==v['native_sha256']and sha(P/'geometry-report.json')==v['geometry_report_sha256']
i=json.loads((PCB/'layout-inspection.json').read_text());c=json.loads((PCB/'circuit-conservation.json').read_text());assert c['all_338_nodes_equal_R16U']
D=A.openDocument(str(nf));rows=[];boards={}
for domain,q in i['boards'].items():
 board=PCB/domain/(domain+'-r23.kicad_pcb');assert sha(board)==q['native_board_sha256']
 o=D.getObject(domain.title()+'PCB_R17');pts=[[g.StartPoint.x,g.StartPoint.y]for g in o.Base.Geometry]
 assert len(pts)==len(q['outline_xy_mm'])
 assert max(abs(a-b)for x,y in zip(pts,q['outline_xy_mm'])for a,b in zip(x,y))<1e-5
 assert abs(o.LengthFwd.Value-q['thickness_mm'])<1e-6
 assert abs(o.Base.Placement.Base.z+.5)<1e-6
 boards[domain]={'native_board_sha256':sha(board),'native_substrate_outline_and_thickness_equal':True,'parts':len(q['placements'])}
 for p in q['placements']:
  if not p['body_xy_mm']:continue
  a,b,u,w=p['body_xy_mm'];z,t=p['z_bounds_mm'];expected=[a,b,z,u,w,t]
  s=D.getObject('R17_'+p['ref']).Shape;b=s.optimalBoundingBox(False,False)
  actual=[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
  delta=max(abs(a-b)for a,b in zip(actual,expected));assert delta<1e-5,p['ref']
  rows.append({'ref':p['ref'],'maximum_bounds_delta_mm':delta})
assert len(rows)==88 and sum(q['parts']for q in boards.values())==89
A.closeDocument(D.Name);assert sha(nf)==r['native_sha256']
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps({'native_CAD_sha256':sha(nf),'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'PCB_inspection_sha256':sha(PCB/'layout-inspection.json'),'circuit_conservation_sha256':sha(PCB/'circuit-conservation.json'),'comparator_sha256':sha(Path(__file__)),'boards':boards,'actual_Fab_height_boxes':rows,'scope':'Exact-current saved CAD substrate/sketch/height and 88 native Fab-height boxes equal current R23D inspection;89main parts/338device nodes conserved by bound circuit report. Not copper/actual terminal, wire/flex, toleranced fit or electrical/physical qualification.'},indent=2)+'\n')
print('Both native substrates/88actual Fab-height boxes equal R23D;89main parts/338nodes bound',flush=True)
