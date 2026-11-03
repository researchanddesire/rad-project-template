"""All saved flange drill circles against actual native copper/paste polygons."""
from pathlib import Path
import sys,json,hashlib
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
P=Path(sys.argv[1]).resolve();source=P/'route-geometry.json';g=json.loads(source.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'flange-r28.kicad_pcb')==g['board_sha256']
pads=[(q,unary_union([Polygon(x)for x in q['polygons']]))for q in g['pads']];rows=[]
for q in g['routes']:
 if q['kind']!='via':continue
 hits=[]
 for a,s in pads:
  d=Point(q['position']).distance(s)
  if d<q['drill']/2-1e-7:hits.append({'ref':a['ref'],'pad':a['number'],'pad_net':a['net'],'copper_layers':a['layers'],'paste_layers':a['paste'],'center_distance_mm':d,'drill_overlap_depth_mm':q['drill']/2-d})
 rows.append({'via':q,'drill_hits':hits})
r={'native_board_sha256':g['board_sha256'],'geometry_sha256':sha(source),'reviewer_sha256':sha(Path(__file__)),'through_vias':len(rows),'native_pad_shapes':len(pads),'vias_drilling_SMD_copper':sum(any(a['copper_layers']for a in q['drill_hits'])for q in rows),'vias_drilling_paste':sum(any(a['paste_layers']for a in q['drill_hits'])for q in rows),'rows':rows,'scope':'Native polygon distances vs drill circles; native paste margins asserted zero at extraction. Not filled/capped/tented vias, stencil, supplier or physical assembly acceptance.'}
(P/'drill-paste-review.json').write_text(json.dumps(r,indent=2)+'\n');print(len(rows),'drills /',len(pads),'pad shapes; copper/paste drill hits',r['vias_drilling_SMD_copper'],r['vias_drilling_paste'],flush=True)
assert r['vias_drilling_SMD_copper']==r['vias_drilling_paste']==0
