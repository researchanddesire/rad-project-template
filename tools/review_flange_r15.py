"""Circuit conservation and all-via copper/paste inventory; read-only."""
from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as E
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();B=ROOT/'hardware/pcb/split-r14/candidate-b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def xml(p):
 r=E.parse(p).getroot();comps={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint'),'libsource':c.find('libsource').attrib}for c in r.findall('components/comp')};nodes={(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'),n.get('pintype'))for net in r.findall('nets/net')for n in net.findall('node')};return comps,nodes
changes=[];domains={}
for domain in ['system','body','flange']:
 old=B/(domain+'-native.xml')if domain=='system'else B/domain/(domain+'-native.xml');new=P/(domain+'-native.xml')if domain=='system'else P/domain/(domain+'-native.xml')
 oc,on=xml(old);nc,nn=xml(new);assert set(oc)==set(nc)and on==nn
 for ref in oc:
  if oc[ref]!=nc[ref]:
   assert ref=='J1'and domain!='body';oldid=oc[ref]['footprint'];newid=nc[ref]['footprint'];assert oldid.endswith('JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal')and newid.endswith('JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal');a=dict(oc[ref]);a['footprint']=newid;assert a==nc[ref];changes.append({'domain':domain,'ref':ref,'old':oldid,'new':newid})
 domains[domain]={'components':len(nc),'pin_net_function_type_nodes':len(nn),'all_nodes_match_R14':True,'old_xml_sha256':sha(old),'new_xml_sha256':sha(new)}
assert len(changes)==2 and sha(P/'body/body-r15.kicad_pcb')==sha(B/'body/body-r14.kicad_pcb')
record={'reviewer_sha256':sha(Path(__file__)),'domain_native_XML_parity':domains,'only_component_field_changes':changes,'body_board_byte_identical_to_R14B':True,'body_board_sha256':sha(P/'body/body-r15.kicad_pcb'),'source_R14_ERC_record_sha256':sha(B/'native-erc.json'),'fresh_R15_native_ERC':False,'ERC_note':'R14 saved full-system ERC is source evidence only; all338pin/net/function/type nodes conserved. R15 only changesJ1footprint and titles/project names; a fresh native GUI ERC was not obtained because the native app observation timed out. No exclusions/rules changed. Not an R15ERC pass.'}
(P/'native-netlist-parity.json').write_text(json.dumps(record,indent=2)+'\n')
gpath=P/'route-geometry.json';g=json.loads(gpath.read_text());bp=P/'flange/flange-r15.kicad_pcb';assert sha(bp)==g['board_sha256'];pads=[]
for p in g['pads']:
 q=dict(p);q['_shape']=unary_union([Polygon(poly)for poly in p['polygons']]);pads.append(q)
rows=[]
for v in g['routes']:
 if v['kind']!='via':continue
 point=Point(v['position']);drill=[];paste=[];annulus=[]
 for p in pads:
  distance=point.distance(p['_shape']);entry={'ref':p['ref'],'pad':p['number'],'pad_net':p['net'],'copper_layers':p['layers'],'paste_layers':p['paste'],'distance_center_to_shape_mm':distance,'drill_overlap_depth_mm':max(0,v['drill']/2-distance)}
  if p['layers']and distance<v['diameter']/2-1e-7:annulus.append(entry)
  if p['layers']and distance<v['drill']/2-1e-7:drill.append(entry)
  if p['paste']and distance<v['drill']/2-1e-7:paste.append(entry)
 rows.append({'net':v['net'],'xy_mm':v['position'],'copper_diameter_mm':v['diameter'],'drill_mm':v['drill'],'annulus_overlaps':annulus,'drill_overlaps_copper':drill,'drill_overlaps_paste':paste})
counts={'all_through_vias':len(rows),'all_native_copper_or_paste_pad_shapes':len(pads),'vias_drilling_SMD_copper':sum(bool(v['drill_overlaps_copper'])for v in rows),'vias_drilling_paste':sum(bool(v['drill_overlaps_paste'])for v in rows)}
inventory={'date':'2026-11-01','reviewer_sha256':sha(Path(__file__)),'native_board_sha256':sha(bp),'native_geometry_sha256':sha(gpath),'counts':counts,'all_vias':rows,'method':'Native GetEffectivePolygon in actual saved top-coordinate frame, all component copper and paste-only shapes. Native paste margin zero asserted at extraction. Circular/rounded shapes use native polygon approximation. Center-to-shape distances compared separately to drill radius and annulus radius. No mask tenting/fill/cap, stencil thickness or received-process acceptance is inferred.'}
(P/'drill-paste-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps({'circuit':domains,'inventory':counts,'drill_in_copper':[{'net':r['net'],'xy':r['xy_mm'],'pads':[(p['ref'],p['pad'])for p in r['drill_overlaps_copper']]}for r in rows if r['drill_overlaps_copper']]},indent=2))
