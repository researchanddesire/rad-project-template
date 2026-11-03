"""All-via drill/paste inventory from actual R17 saved native polygons."""
from pathlib import Path
import sys,json,hashlib
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();gp=P/'body-native-geometry-all-layers.json';g=json.loads(gp.read_text());bp=next((P/'body').glob('body-r*.kicad_pcb'));assert sha(bp)==g['board_sha256'];pads=[(p,unary_union([Polygon(poly)for poly in p['polygons']]))for p in g['pads']];rows=[]
for v in g['routes']:
 if v['kind']!='via':continue
 point=Point(v['position']);drill=[];paste=[];annulus=[]
 for p,s in pads:
  d=point.distance(s);entry={'ref':p['ref'],'pad':p['number'],'pad_net':p['net'],'copper_layers':p['layers'],'paste_layers':p['paste'],'distance_center_to_shape_mm':d,'drill_overlap_depth_mm':max(0,v['drill']/2-d)}
  if p['layers']and d<v['diameter']/2-1e-7:annulus.append(entry)
  if p['layers']and d<v['drill']/2-1e-7:drill.append(entry)
  if p['paste']and d<v['drill']/2-1e-7:paste.append(entry)
 rows.append({'net':v['net'],'xy_mm':v['position'],'diameter_mm':v['diameter'],'drill_mm':v['drill'],'annulus_overlaps':annulus,'drill_overlaps_copper':drill,'drill_overlaps_paste':paste})
counts={'all_through_vias':len(rows),'all_native_copper_or_paste_pad_shapes':len(pads),'vias_drilling_SMD_copper':sum(bool(v['drill_overlaps_copper'])for v in rows),'vias_drilling_paste':sum(bool(v['drill_overlaps_paste'])for v in rows)};out={'date':'2026-11-01','reviewer_sha256':sha(Path(__file__)),'native_board_sha256':sha(bp),'native_geometry_sha256':sha(gp),'counts':counts,'all_vias':rows,'scope':'Actual native GetEffectivePolygon approximations, including paste-only shapes. Zero native paste margins asserted by extractor. No hole filling/capping/tenting, stencil, process or received-part acceptance.'};(P/'drill-paste-inventory.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(counts),flush=True);assert not counts['vias_drilling_SMD_copper']and not counts['vias_drilling_paste']
